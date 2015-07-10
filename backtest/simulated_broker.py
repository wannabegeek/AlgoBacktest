import logging
from strategycontainer.order import StopLoss, Direction, State, Entry, Order
from strategycontainer.ordermanager import OrderManager, OrderbookException
from strategycontainer.position import Position
from strategycontainer.price import Tick

class Broker(OrderManager):

    def __init__(self):
        self.orders = []
        self.positions = []
        self.currentTick = None
        self.orderStatusObservers = []
        self.positionObservers = []

    def placeOrder(self, order):
        if not isinstance(order, Order):
            raise ValueError('argument "order" must be a Order')

        try:
            self.orders.append(order)
            self._evaluateOrdersStatus(order, self.currentTick)
        except KeyError:
            raise OrderbookException("Order not found")

    def modifyOrder(self, order):
        if not isinstance(order, Order):
            raise ValueError('argument "order" must be a Order')

        if order in self.orders:
            # we shouldn't need to do anything else, since the reference will have been updated
            self._evaluateOrdersStatus(order, self.currentTick)
        else:
            raise OrderbookException("Order not found")

    def cancelOrder(self, order):
        if not isinstance(order, Order):
            raise ValueError('argument "order" must be a Order')
        try:
            self.orders.remove(order)
        except ValueError:
            raise OrderbookException("Order not found")

    def closePosition(self, position):
        if not isinstance(position, Position):
            raise ValueError('argument "position" must be a Position')

        self._closePositionAndNotifyClient(position, self.currentTick, Position.ExitReason.CLOSED)


    def addOrderStatusObserver(self, observer):
        self.orderStatusObservers.append(observer)

    def addPositionObserver(self, observer):
        self.positionObservers.append(observer)

    def handleTickUpdate(self, symbol, tick):
        try:
            # We need to evaluate if we have any limit orders and stop loss events triggered
            self._evaluatePendingOrder(tick)
            self._evaluateActivePositions(tick)
            self.priceConflation[symbol].addTick(tick)
        except KeyError as e:
            logging.error("Received data update for symbol we're not subscribed to (%s)" % (symbol,))

    def _evaluatePendingOrder(self, tick):
        for order in self.orders:
            if self._evaluateOrdersStatus(order, tick):
                position = Position(order, tick)
                #TODO: Create position and notify client (ordersStatusObservers & positionObservers)
                self.context.openPosition(position)
                logging.debug("Opened position for %s" % position)

    def _evaluateActivePositions(self, tick):
        for position in self.positions:
            reason = self._shouldClosePosition(position, tick)
            if reason is not Position.ExitReason.NOT_CLOSED:
                logging.debug("Position %s has been closed due to %s" % (position, reason.name))

    def _evaluateOrdersStatus(self, order, tick):
        if not isinstance(order, Order):
            raise ValueError('argument "order" must be a Order')
        if not isinstance(tick, Tick):
            raise ValueError('argument "tick" must be a Tick')

        if order.isComplete():
            raise RunTimeError("Order is already complete")

        if order.expireTime is not None:
            timediff = tick.timestamp - order.entryTime
            if timediff.total_seconds() >= order.expireTime.total_seconds():
                order.state = State.EXPIRED
                return False

        if order.entry.type == Entry.Type.MARKET:
            return True
        elif order.entry.type == Entry.Type.LIMIT:
            if order.direction == Direction.LONG:
                return tick.offer <= order.entry.price
            elif order.direction == Direction.SHORT:
                return tick.bid >= order.entry.price
        elif order.entry.type == Entry.Type.STOP_ENTRY:
            if order.direction == Direction.LONG:
                return tick.offer >= order.entry.price
            elif order.direction == Direction.SHORT:
                return tick.bid <= order.entry.price

        return False


    def _closePositionAndNotifyClient(self, position, tick, reason):
        position.close(tick, reason)
        del(self.positions[position])
        #TODO: Notify the client (positionObservers)
        logging.debug("Position %s close" % (position,))

    def _shouldClosePosition(self, position, tick):
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
                        self._closePositionAndNotifyClient(position, tick, Position.ExitReason.STOP_LOSS)
                else:
                    if tick.bid >= position.stopPrice:
                        # logging.debug("Position %s hit its stop loss (tick %s)" % (self, tick))
                        self._closePositionAndNotifyClient(position, tick, Position.ExitReason.STOP_LOSS)

            if position.order.takeProfit is not None:
                if position.order.direction == Direction.LONG and tick.offer >= position.takeProfit:
                    # logging.debug("Position %s hit its take profit target (tick %s)" % (self, tick))
                    self._closePositionAndNotifyClient(position, tick, Position.ExitReason.TAKE_PROFIT)
                elif position.order.direction == Direction.SHORT and tick.bid <= position.takeProfit:
                    # logging.debug("Position %s hit its take profit target (tick %s)" % (self, tick))
                    self._closePositionAndNotifyClient(position, tick, Position.ExitReason.TAKE_PROFIT)

        return position.exitReason
