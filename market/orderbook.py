import logging

from market.interfaces.orderrouter import OrderRouter
from market.order import State
from market.position import Position


class OrderBook(object):
    def __init__(self, order_router):
        if not isinstance(order_router, OrderRouter):
            raise TypeError("order_router must be OrderRouter type")

        self.order_router = order_router
        self.containers = []
        self.order_router.addOrderStatusObserver(self.orderStatus)
        self.order_router.addPositionObserver(self.positionStatus)
        self.orders = {}
        self.positions = {}
        self.orderObservers = {}
        self.positionObservers = {}

    def addOrderStatusObserver(self, context, callback):
        if context in self.orderObservers:
            self.orderObservers[context].append(callback)
        else:
            self.orderObservers[context] = [callback, ]

    def addPositionStatusObserver(self, context, callback):
        if context in self.positionObservers:
            self.positionObservers[context].append(callback)
        else:
            self.positionObservers[context] = [callback, ]

    def orderStatus(self, order, previousState):
        try:
            callbacks = self.orderObservers[order.context]
            for callback in callbacks:
                callback(order, previousState)
        except KeyError:
            # there isn't an observer
            pass

        if order.state is State.WORKING:
            if previousState is State.PENDING_NEW:
                logging.debug("Order has been accepted")
            elif previousState is State.PENDING_MODIFY:
                logging.debug("Modify has been accepted")
            elif previousState is State.PENDING_CANCEL:
                logging.debug("Cancel has been accepted")
        elif order.isComplete() is True:
            # we need to remove the order from the order book since it is complete
            del(self.orders[order.id])

    def registerPosition(self, position):
        pass

    def positionStatus(self, position, previousState):
        try:
            callbacks = self.positionObservers[position.order.context]
            for callback in callbacks:
                callback(position, previousState)
        except KeyError:
            # there isn't an observer
            pass

        if position.status is Position.PositionStatus.OPEN:
            self.positions[position.id] = position
            self.registerPosition(position)
        elif not position.isOpen():
            logging.debug("Position has been closed")
            del(self.positions[position.id])

    def placeOrder(self, context, order):
        # send new order to market
        order.context = context
        if self._checkRiskLimits(context, order):
            self.orders[order.id] = order
            self.order_router.placeOrder(order)
        else:
            logging.error("Risk limits breached rejecting request")
            callbacks = self.orderObservers[context]
            previousState = order.state
            order.state = State.REJECTED
            for callback in callbacks:
                callback(order, previousState)


    def modifyOrder(self, order):
        # modify order on market
        # find the original context
        context = self.orders[order.id][1]
        if self._checkRiskLimits(context, order):
            order.state = State.PENDING_MODIFY
            self.order_router.modifyOrder(order)
        else:
            logging.error("Risk limits breached rejecting request")
            callbacks = self.orderObservers[context]
            previousState = order.state
            order.state = State.REJECTED
            for callback in callbacks:
                callback(order, previousState)
            order.state = State.WORKING


    def cancelOrder(self, order):
        # cancel order on market
        order.state = State.PENDING_CANCEL
        self.order_router.cancelOrder(order)
        del(self.orders[order.id])

    def closePosition(self, position):
        self.order_router.closePosition(position)


    def _checkRiskLimits(self, container, order):
        # do container specific checks
        # do overall risk checks
        return True


class MultiThreadedOrderBook(OrderBook):
    pass

class BacktestOrderbook(OrderBook):

    def __init__(self, order_router):
        super(BacktestOrderbook, self).__init__(order_router)
        self.containerPositions = []

    def registerPosition(self, position):
        self.containerPositions.append(position)

    def __str__(self):
        totalPositions = len(list(filter(lambda x: not x.isOpen(), self.containerPositions)))

        closed = list(map(lambda x: "%s  --> %.2fpts (%s)" % (x, x.pointsDelta(), x.positionTime()), filter(lambda x: not x.isOpen(), self.containerPositions)))
        open = list(map(lambda x: "%s" % (x), filter(lambda x: x.isOpen(), self.containerPositions)))
        winning = list(filter(lambda x: x.pointsDelta() > 0.0, filter(lambda x: not x.isOpen(), self.containerPositions)))

        return "Completed:\n%s\nOpen:\n%s\nWinning Ratio: %.2f%%\nTotal Pts: %.2f" % ("\n".join(closed),
                                                                   "\n".join(open),
                                                                   (len(winning)/totalPositions * 100),
                                                                   sum([x.pointsDelta() for x in filter(lambda x: not x.isOpen(), self.containerPositions)]))

    __repr__ = __str__