from abc import ABCMeta, abstractmethod


class OrderbookException(Exception):
    pass

class OrderRouter(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.orderStatusObservers = []
        self.positionObservers = []

    @abstractmethod
    def placeOrder(self, order):
        # send new order to market
        pass

    @abstractmethod
    def modifyOrder(self, order):
        # modify order on market
        pass

    @abstractmethod
    def cancelOrder(self, order):
        # cancel order on market
        pass

    @abstractmethod
    def closePosition(self, position):
        pass

    def addOrderStatusObserver(self, observer):
        self.orderStatusObservers.append(observer)

    def addPositionObserver(self, observer):
        self.positionObservers.append(observer)

