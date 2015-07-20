import logging

from data.data_provider import Provider
from market.interfaces.data_provider import DataProvider
from market.order import StopLoss, Direction, State, Entry, Order
from market.interfaces.orderrouter import OrderRouter, OrderbookException
from market.position import Position
from market.price import Tick


class Broker(OrderRouter, DataProvider):

    def __init__(self, priceDataProvider):
        if not isinstance(priceDataProvider, Provider):
            raise TypeError("priceDataProvider must be a subclass of data.data_provider.Provider")

        self.priceDataProvider = priceDataProvider
        self.currentTick = None

        OrderRouter.__init__(self)
        DataProvider.__init__(self)
        self.orders = []
        self.positions = []

    def start(self):
        self.priceDataProvider.startPublishing(lambda symbol, tick: self._handleTickUpdate(symbol, tick))

    def placeOrder(self, order):
        if not isinstance(order, Order):
            raise TypeError('argument "order" must be a Order')

        if order.state is not State.PENDING_NEW:
            raise ValueError("Attempting to place a non-pending order")

        self.orders.append(order)

        order.state = State.WORKING
        [f(order, State.PENDING_NEW) for f in self.orderStatusObservers]
        self._evaluateOrdersStatus(order, self.currentTick)

    def modifyOrder(self, order):
        if not isinstance(order, Order):
            raise TypeError('argument "order" must be a Order')
        if order.state is not State.PENDING_MODIFY:
            raise ValueError("Attempting to modify a non-pending order")

        order.state = State.WORKING
        [f(order, State.PENDING_MODIFY) for f in self.orderStatusObservers]
        if order in self.orders:
            # we shouldn't need to do anything else, since the reference will have been updated
            self._evaluateOrdersStatus(order, self.currentTick)
        else:
            raise OrderbookException("Order not found")

    def cancelOrder(self, order):
        if not isinstance(order, Order):
            raise TypeError('argument "order" must be a Order')
        if order.state is not State.PENDING_CANCEL:
            raise ValueError("Attempting to cancel a non-pending order")

        try:
            self.orders.remove(order)
            order.state = State.CANCELLED
            [f(order, State.PENDING_CANCEL) for f in self.orderStatusObservers]
        except ValueError:
            raise OrderbookException("Order not found")

    def closePosition(self, position):
        if not isinstance(position, Position):
            raise TypeError('argument "position" must be a Position')

        self._closePosition(position, self.currentTick, Position.PositionStatus.CLOSED)

    def _handleTickUpdate(self, symbol, tick):
        try:
            # We need to evaluate if we have any limit orders and stop loss events triggered
            self._processPendingOrders(tick)
            self._evaluateOpenPositions(tick)
            self.currentTick = tick
            self._notifyObservers(symbol, tick)
        except KeyError as e:
            logging.error("Received data update for symbol we're not subscribed to (%s)" % (symbol,))

    def _processPendingOrders(self, tick):
        for order in self.orders:
            self._evaluateOrdersStatus(order, tick)

    def _fillOrder(self, order, tick):
        previousState = order.state
        #Create position and notify client (ordersStatusObservers & positionObservers)
        order.state = State.FILLED
        self.orders.remove(order)
        #TODO we should filter the observers to the observers related to the position/order
        [f(order, previousState) for f in self.orderStatusObservers]
        position = Position(order, tick)
        [f(position, None) for f in self.positionObservers]
        self.positions.append(position)
        logging.debug("Opened position for %s" % position)
        # we're not interested in the order anymore, only the position

    def _evaluateOrdersStatus(self, order, tick):
        previousState = order.state
        if not isinstance(order, Order):
            raise TypeError('argument "order" must be a Order')
        if not isinstance(tick, Tick):
            raise TypeError('argument "tick" must be a Tick')

        if order.isComplete():
            raise OrderbookException("Order is already complete")

        if order.expireTime is not None:
            timeSinceCreation = tick.timestamp - order.entryTime
            if timeSinceCreation.total_seconds() >= order.expireTime.total_seconds():
                order.state = State.EXPIRED
                [f(order, previousState) for f in self.orderStatusObservers]
                self.orders.remove(order)

        if order.entry.type == Entry.Type.MARKET:
            self._fillOrder(order, tick)
        elif order.entry.type == Entry.Type.LIMIT:
            if order.direction == Direction.LONG and tick.offer <= order.entry.price:
                self._fillOrder(order, tick)
            elif order.direction == Direction.SHORT and tick.bid >= order.entry.price:
                self._fillOrder(order, tick)
        elif order.entry.type == Entry.Type.STOP_ENTRY:
            if order.direction == Direction.LONG and tick.offer >= order.entry.price:
                self._fillOrder(order, tick)
            elif order.direction == Direction.SHORT and tick.bid <= order.entry.price:
                self._fillOrder(order, tick)

    def _evaluateOpenPositions(self, tick):
        for position in self.positions:
            self._evaluateOpenPosition(position, tick)

    def _closePosition(self, position, tick, reason):
        previousState = position.status
        position.close(tick, reason)
        #Notify the client (positionObservers)
        self.positions.remove(position)
        #TODO we should filter the observers to the observers related to the position/order
        [f(position, previousState) for f in self.positionObservers]
        logging.debug("Position %s has been closed due to %s" % (position, position.status.name))

    def _evaluateOpenPosition(self, position, tick):
        if not isinstance(position, Position):
            raise ValueError('argument "position" must be a Position')
        if not isinstance(tick, Tick):
            raise ValueError('argument "tick" must be a Tick')

        if position.isOpen():
            if position.order.stoploss is not None:
                if position.order.stoploss.type == StopLoss.Type.TRAILING:
                    if position.order.direction == Direction.LONG:
                        position.stopPrice = max(position.stopPrice, tick.bid - position.order.stoploss.points * position.order.symbol.lot_size)
                    else:
                        position.stopPrice = min(position.stopPrice, tick.offer + position.order.stoploss.points * position.order.symbol.lot_size)

                if position.order.direction == Direction.LONG:
                    if tick.offer <= position.stopPrice:
                        # logging.debug("Position %s hit its stop loss (tick %s)" % (self, tick))
                        self._closePosition(position, tick, Position.PositionStatus.STOP_LOSS)
                else:
                    if tick.bid >= position.stopPrice:
                        # logging.debug("Position %s hit its stop loss (tick %s)" % (self, tick))
                        self._closePosition(position, tick, Position.PositionStatus.STOP_LOSS)

            if position.order.takeProfit is not None:
                if position.order.direction == Direction.LONG and tick.offer >= position.takeProfit:
                    # logging.debug("Position %s hit its take profit target (tick %s)" % (self, tick))
                    self._closePosition(position, tick, Position.PositionStatus.TAKE_PROFIT)
                elif position.order.direction == Direction.SHORT and tick.bid <= position.takeProfit:
                    # logging.debug("Position %s hit its take profit target (tick %s)" % (self, tick))
                    self._closePosition(position, tick, Position.PositionStatus.TAKE_PROFIT)

        return position.status
