from abc import ABCMeta, abstractmethod
import datetime


class MarketDataPeriod(object):
    MIN_1 = datetime.timedelta(seconds=60)
    MIN_5 = datetime.timedelta(seconds=300)
    MIN_10 = datetime.timedelta(seconds=600)
    MIN_15 = datetime.timedelta(seconds=900)
    MIN_30 = datetime.timedelta(seconds=1800)
    HOUR_1 = datetime.timedelta(seconds=3600)
    HOUR_2 = datetime.timedelta(seconds=7200)
    HOUR_4 = datetime.timedelta(seconds=14400)
    DAY = datetime.timedelta(seconds=86400)
    WEEK = datetime.timedelta(seconds=604800)

class MarketDataException(Exception):
    pass

class DataProvider(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.currentTick = None
        self.priceObservers = {}

    def start(self):
        self.priceDataProvider.startPublishing(lambda symbol, tick: self._handleTickUpdate(symbol, tick))

    def addPriceObserver(self, symbol, observer):
        if symbol not in self.priceObservers:
            self.priceObservers[symbol] = [observer,]
        else:
            self.priceObservers[symbol].append(observer)
