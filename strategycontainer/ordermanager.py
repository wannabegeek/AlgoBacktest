from abc import ABCMeta, abstractmethod

class OrderbookException(Exception):
    pass

class OrderManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def placeOrder(self, order):
        # send new order to markete
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

    @abstractmethod
    def addOrderStatusObserver(self, observer):
        pass

    @abstractmethod
    def addPositionObserver(self, observer):
        pass

