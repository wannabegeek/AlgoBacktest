from abc import ABCMeta, abstractmethod
from market.interfaces.data_provider import DataProvider


class MarketDataException(Exception):
    pass

class MarketData(object):
    __metaclass__ = ABCMeta

    def __init__(self, data_provider):
        if not isinstance(data_provider, DataProvider):
            raise TypeError("data_provider must be a subclass of DataProvider")

        self.data_provider = data_provider

        self.currentTick = None
        self.priceObservers = {}

    @abstractmethod
    def _handleTickUpdate(self, symbol, tick):
        pass

    def start(self):
        self.data_provider.startPublishing(lambda symbol, tick: self._handleTickUpdate(symbol, tick))

    def addPriceObserver(self, symbol, observer):
        if symbol not in self.priceObservers:
            self.priceObservers[symbol] = [observer,]
        else:
            self.priceObservers[symbol].append(observer)
