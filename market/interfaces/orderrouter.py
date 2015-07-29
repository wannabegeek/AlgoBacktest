from abc import ABCMeta, abstractmethod


class OrderbookException(Exception):
    pass

class OrderRouter(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.orderStatusObservers = []
        self.positionObservers = []

    @abstractmethod
    def place_order(self, order):
        # send new order to market
        pass

    @abstractmethod
    def modify_order(self, order):
        # modify order on market
        pass

    @abstractmethod
    def cancel_order(self, order):
        # cancel order on market
        pass

    @abstractmethod
    def close_position(self, position):
        pass

    def addOrderStatusObserver(self, observer):
        self.orderStatusObservers.append(observer)

    def addPositionObserver(self, observer):
        self.positionObservers.append(observer)

