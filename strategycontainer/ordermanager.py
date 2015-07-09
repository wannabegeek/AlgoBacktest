from abc import ABCMeta, abstractmethod

class OrderManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def newOrder(self, order):
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
    def cancelPosition(self, position):
        pass