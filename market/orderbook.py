import logging
import weakref

from market.interfaces.orderrouter import OrderRouter
from market.order import Order, State
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

    def orderStatus(self, order, previousState):
        if order.state is State.WORKING:
            if previousState is State.PENDING_NEW:
                logging.debug("Order has been accepted")
            elif previousState is State.PENDING_MODIFY:
                logging.debug("Order has been accepted")
            elif previousState is State.PENDING_CANCEL:
                logging.debug("Order has been accepted")
        elif order.isComplete() is True:
            # we need to remove the order from the order book since it is complete
            del(self.orders[order.id])

    def registerPosition(self, position):
        pass

    def positionStatus(self, position, previousState):
        if position.status is Position.PositionStatus.OPEN:
            self.positions[position.id] = position
            self.registerPosition(position)
        elif not position.isOpen():
            logging.debug("Position has been closed")
            del(self.positions[position.id])

    def placeOrder(self, container, order):
        # send new order to market
        if self._checkRiskLimits(container, order):
            self.order_router.placeOrder(order)
            self.orders[order.id] = (order, container)
        else:
            logging.error("Risk limits breached rejecting request")

    def modifyOrder(self, container, order):
        # modify order on market
        if self._checkRiskLimits(container, order):
            order.state = State.PENDING_MODIFY
            self.order_router.modifyOrder(order)
        else:
            logging.error("Risk limits breached rejecting request")

    def cancelOrder(self, container, order):
        # cancel order on market
        order.state = State.PENDING_CANCEL
        self.order_router.cancelOrder(order)
        del(self.orders[order.id])

    def closePosition(self, container, position):
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
        ps = map(lambda x: "%s  --> %spts" % (x, x.pointsDelta()), filter(lambda x: not x.isOpen(), self.containerPositions))
        return "\n".join(ps)

    __repr__ = __str__