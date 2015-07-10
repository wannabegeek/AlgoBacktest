import logging
from strategycontainer.order import StopLoss, Direction, State, Entry, Order
from strategycontainer.ordermanager import OrderManager, OrderbookException
from strategycontainer.position import Position
from strategycontainer.price import Tick

class Broker(OrderManager):

    def __init__(self, priceDataProvider):
        self.priceDataProvider = priceDataProvider
        self.orders = []
        self.positions = []
        self.currentTick = None
        self.orderStatusObservers = []
        self.positionObservers = []
        self.priceObservers = {}

    def start(self):
        self.priceDataProvider.startPublishing(lambda symbol, tick: self._handleTickUpdate(symbol, tick))

    def placeOrder(self, order):
        if not isinstance(order, Order):
            raise TypeError('argument "order" must be a Order')

        try:
            self.orders.append(order)
            self._evaluateOrdersStatus(order, self.currentTick)
        except KeyError:
            raise OrderbookException("Order not found")

    def modifyOrder(self, order):
        if not isinstance(order, Order):
            raise TypeError('argument "order" must be a Order')

        if order in self.orders:
            # we shouldn't need to do anything else, since the reference will have been updated
            self._evaluateOrdersStatus(order, self.currentTick)
        else:
            raise OrderbookException("Order not found")

    def cancelOrder(self, order):
        if not isinstance(order, Order):
            raise TypeError('argument "order" must be a Order')
        try:
            self.orders.remove(order)
        except ValueError:
            raise OrderbookException("Order not found")

    def closePosition(self, position):
        if not isinstance(position, Position):
            raise TypeError('argument "position" must be a Position')

        self._closePosition(position, self.currentTick, Position.PositionStatus.CLOSED)

    def addOrderStatusObserver(self, observer):
        self.orderStatusObservers.append(observer)

    def addPositionObserver(self, observer):
        self.positionObservers.append(observer)

    def addPriceObserver(self, symbol, observer):
        if symbol not in self.priceObservers:
            self.priceObservers[symbol] = [observer,]
        else:
            self.priceObservers[symbol].append(observer)

    def _handleTickUpdate(self, symbol, tick):
        try:
            # We need to evaluate if we have any limit orders and stop loss events triggered
            self._processPendingOrders(tick)
            self._evaluateOpenPositions(tick)
            if symbol in self.priceObservers:
                for observer in self.priceObservers[symbol]:
                    observer(symbol, tick)
        except KeyError as e:
            logging.error("Received data update for symbol we're not subscribed to (%s)" % (symbol,))

    def _processPendingOrders(self, tick):
        for order in self.orders:
            self._evaluateOrdersStatus(order, tick)

    def _fillOrder(self, order, tick):
        #Create position and notify client (ordersStatusObservers & positionObservers)
        self.orders.remove(order)
        [f(order, State.FILLED) for f in self.orderStatusObservers]
        position = Position(order, tick)
        [f(position, Position.PositionStatus.OPEN) for f in self.positionObservers]
        logging.debug("Opened position for %s" % position)
        # we're not interested in the order anymore, only the position

    def _evaluateOrdersStatus(self, order, tick):
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
                [f(order, State.EXPIRED) for f in self.orderStatusObservers]
                self.orders.remove(order)

        if order.entry.type == Entry.Type.MARKET:
            self._fillOrder(order, tick)
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
        position.close(tick, reason)
        #Notify the client (positionObservers)
        self.positions.remove(position)
        [f(position, position.exitReason) for f in self.positionObservers]
        logging.debug("Position %s has been closed due to %s" % (position, position.exitReason.name))

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
