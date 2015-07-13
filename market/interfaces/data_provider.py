from abc import ABCMeta, abstractmethod
import logging


class DataProvider(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.priceObservers = []
        self.subscribedSymbols = []

    @abstractmethod
    def subscribeSymbol(self, symbol):
        self.subscribedSymbols.append(symbol)

    @abstractmethod
    def unsubscribe(self, symbol):
        self.subscribedSymbols.remove(symbol)

    def addPriceObserver(self, observer):
        self.priceObservers.append(observer)

    def removePriceObserver(self, observer):
        self.priceObservers.remove(observer)

    def _notifyObservers(self, symbol, tick):
        if symbol not in self.subscribedSymbols:
            logging.error("Received price data for something we're not interested in")
        else:
            for observer in self.priceObservers:
                observer(symbol, tick)