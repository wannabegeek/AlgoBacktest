import logging

from market.interfaces.orderrouter import OrderRouter


class OrderBook(object):
    def __init__(self, order_router):
        if not isinstance(order_router, OrderRouter):
            raise TypeError("order_router must be OrderRouter type")

        self.order_router = order_router
        self.containers = []

    def addContainer(self, container):
        self.containers.append(container)

    def removeContainer(self, container):
        """
        L.removeContainer(container) -> None -- remove container from orderbook.
        Raises ValueError if the container is not present.
        """
        self.containers.remove(container)

    def enableContainer(self, container):
        pass

    def disableContainer(self, container):
        pass



    def placeOrder(self, container, order):
        # send new order to market
        if self._checkRiskLimits(container, order):
            self.order_router.placeOrder(order)
        else:
            logging.error("Risk limits breached rejecting request")

    def modifyOrder(self, container, order):
        # modify order on market
        if self._checkRiskLimits(container, order):
            self.order_router.placeOrder(order)
        else:
            logging.error("Risk limits breached rejecting request")

    def cancelOrder(self, container, order):
        # cancel order on market
        self.order_router.cancelOrder(order)

    def closePosition(self, container, position):
        self.order_router.closePosition(position)


    def _checkRiskLimits(self, container, order):
        # do container specific checks
        # do overall risk checks
        return True