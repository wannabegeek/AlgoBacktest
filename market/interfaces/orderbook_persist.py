from abc import ABCMeta, abstractmethod

class OrderbookPersist(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def recover_open_orders(self):
        pass

    @abstractmethod
    def recover_open_positions(self):
        pass

    @abstractmethod
    def add_order(self, order):
        pass

    @abstractmethod
    def update_order(self, order):
        pass

    @abstractmethod
    def add_position(self, position):
        pass

    @abstractmethod
    def update_position(self, position):
        pass
