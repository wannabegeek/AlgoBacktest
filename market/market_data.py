from enum import Enum
import logging
import datetime
from market.interfaces.data_provider import DataProvider
from market.symbol import Symbol


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

class MarketData(object):

    def __init__(self, data_provider):
        if not isinstance(data_provider, DataProvider):
            raise TypeError("data_provider must be a subclass of DataProvider")

        self.data_provider = data_provider
        self.data_provider.addPriceObserver(self.handleTickUpdate)

        self.currentTick = None
        self.priceObservers = {}

    def _observerKey(self, symbol, period):
        return "%s_%s" % (symbol, period.name)

    def addPriceObserver(self, symbol, period, observer):
        if not isinstance(symbol, Symbol):
            raise TypeError("symbol must be Symbol")
        if not isinstance(period, MarketDataPeriod):
            raise TypeError("period must be MarketDataPeriod")

        observerKey = self._observerKey(symbol, period)
        if observerKey not in self.priceObservers:
            self.priceObservers[observerKey] = [observer,]
            self.data_provider.subscribedSymbols(symbol)
        else:
            self.priceObservers[symbol].append(observer)

    def removePriceObserver(self, symbol, period, observer):
        observerKey = self._observerKey(symbol, period)
        for observers in self.priceObservers[observerKey]:
            observers.remove(observer)
            if len(observers) == 0:
                self.data_provider.unsubscribe(symbol)
                del(self.priceObservers[observerKey])

    def handleTickUpdate(self, symbol, tick):
        # we probably need to conflate prices to bake available to algorithms
        try:
            self.priceConflation[symbol].addTick(tick)
        except KeyError as e:
            logging.error("Received data update for symbol we're not subscribed to (%s)" % (symbol,))

