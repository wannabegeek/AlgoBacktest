from abc import ABCMeta, abstractmethod
from data.data_provider import Provider


class OrderbookException(Exception):
    pass

class OrderManager(object):
    __metaclass__ = ABCMeta

    def __init__(self, priceDataProvider):
        if not isinstance(priceDataProvider, Provider):
            raise TypeError("priceDataProvider must be a subclass of data.data_provider.Provider")

        self.priceDataProvider = priceDataProvider

        self.currentTick = None
        self.orderStatusObservers = []
        self.positionObservers = []
        self.priceObservers = {}

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
    def _handleTickUpdate(self, symbol, tick):
        pass


    def start(self):
        self.priceDataProvider.startPublishing(lambda symbol, tick: self._handleTickUpdate(symbol, tick))

    def addOrderStatusObserver(self, observer):
        self.orderStatusObservers.append(observer)

    def addPositionObserver(self, observer):
        self.positionObservers.append(observer)

    def addPriceObserver(self, symbol, observer):
        if symbol not in self.priceObservers:
            self.priceObservers[symbol] = [observer,]
        else:
            self.priceObservers[symbol].append(observer)
