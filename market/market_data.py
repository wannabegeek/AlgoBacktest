import logging
import datetime
from market.interfaces.data_provider import DataProvider
from market.price import Quote, Tick
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

class MarketDataObserver(object):
    def __init__(self, symbol, period, observer = None):
        self.observers = []
        self.priceConflation = PriceConflator(symbol, period, self.quoteHandler)
        if observer is not None:
            self.addObserver(observer)

    def addObserver(self, observer):
        self.observers.append(observer)

    def removeObserver(self, observer):
        self.observers.remove(observer)

    def addTick(self, tick):
        self.priceConflation.addTick(tick)

    def quoteHandler(self, quote):
        for observer in self.observers:
            observer(self.priceConflation.symbol, quote)

class MarketData(object):
    def __init__(self, data_provider):
        if not isinstance(data_provider, DataProvider):
            raise TypeError("data_provider must be a subclass of DataProvider")

        self.data_provider = data_provider
        self.data_provider.addPriceObserver(self.handleTickUpdate)

        self.currentTick = None
        self.priceObservers = {}

    def addPriceObserver(self, symbol, period, observer):
        if not isinstance(symbol, Symbol):
            raise TypeError("symbol must be Symbol")
        if not isinstance(period, datetime.timedelta):
            raise TypeError("period must be timedelta")

        logging.debug("Adding observer of price updates in %s, period %s" % (symbol, period))
        if symbol not in self.priceObservers:
            self.priceObservers[symbol] = {period: MarketDataObserver(symbol, period, observer)}
            self.data_provider.subscribeSymbol(symbol)
        else:
            if period not in self.priceObservers[symbol]:
                self.priceObservers[symbol][period] = MarketDataObserver(symbol, period, observer)
            else:
                self.priceObservers[symbol][period].addObserver(observer)

    def removePriceObserver(self, symbol, period, observer):
        self.priceObservers[symbol][period].remove(observer)
        logging.debug("Removing observer of price updates in %s, period %s" % (symbol, period))
        if len(self.priceObservers[symbol][period]) == 0:
            self.data_provider.unsubscribe(symbol)
            del(self.priceObservers[symbol][period])

    def handleTickUpdate(self, symbol, tick):
        # we probably need to conflate prices to bake available to algorithms
        try:
            for conflationHandlers in self.priceObservers[symbol].values():
                conflationHandlers.addTick(tick)
        except KeyError as e:
            logging.error("Received data update for symbol we're not subscribed to (%s)" % (symbol,))

def roundDateTimeToPeriod(timestamp, period):
    seconds = timestamp.timestamp() % period.total_seconds()
    return timestamp - datetime.timedelta(seconds=seconds)

class PriceConflator(object):
    def __init__(self, symbol, period, callback = None):
        if not isinstance(period, datetime.timedelta):
            raise TypeError("period must be a timedelta")
        self.symbol = symbol
        self.period = period
        self.callback = callback
        self.periodStartingTimestamp = None
        self.currentQuote = None

    def addTick(self, tick):
        if not self.currentQuote:
            self.periodStartingTimestamp = tick.timestamp
            self.currentQuote = Quote(self.symbol, roundDateTimeToPeriod(tick.timestamp, self.period), self.period, tick)
            return self.currentQuote
        else:
            currentTickTimeBlock = roundDateTimeToPeriod(tick.timestamp, self.period)
            currentTickTimestamp = currentTickTimeBlock.timestamp()
            if currentTickTimestamp < (self.currentQuote.startTime + self.period).timestamp():
                self.currentQuote.addTick(tick)
            else:
                if self.callback is not None:
                    self.callback(self.currentQuote)
                t = self.currentQuote.startTime + self.period
                while currentTickTimestamp >= (t + self.period).timestamp():
                        self.callback(Quote(self.symbol, t, self.period, Tick(self.currentQuote.startTime, self.currentQuote.close, self.currentQuote.close)))
                        t = t + self.period
                self.currentQuote = Quote(self.symbol, t, self.period, tick)
                return self.currentQuote
        return None
