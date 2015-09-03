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
        self.price_conflation = PriceConflator(symbol, period, self.quote_handler)
        if observer is not None:
            self.add_observer(observer)

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def add_tick(self, tick):
        self.price_conflation.add_tick(tick)

    def quote_handler(self, quote):
        for observer in self.observers:
            observer(self.price_conflation.symbol, quote)

class MarketData(object):
    def __init__(self, data_provider):
        if not isinstance(data_provider, DataProvider):
            raise TypeError("data_provider must be a subclass of DataProvider")

        self.data_provider = data_provider
        self.data_provider.addPriceObserver(self.tick_update)

        self.current_tick = None
        self.price_observers = {}

    def addPriceObserver(self, symbol, period, observer):
        if not isinstance(symbol, Symbol):
            raise TypeError("symbol must be Symbol")
        if not isinstance(period, datetime.timedelta):
            raise TypeError("period must be timedelta")

        logging.debug("Adding observer of price updates in %s, period %s" % (symbol, period))
        if symbol not in self.price_observers:
            self.price_observers[symbol] = {period: MarketDataObserver(symbol, period, observer)}
            self.data_provider.subscribeSymbol(symbol)
        else:
            if period not in self.price_observers[symbol]:
                self.price_observers[symbol][period] = MarketDataObserver(symbol, period, observer)
            else:
                self.price_observers[symbol][period].add_observer(observer)

    def removePriceObserver(self, symbol, period, observer):
        self.price_observers[symbol][period].remove(observer)
        logging.debug("Removing observer of price updates in %s, period %s" % (symbol, period))
        if len(self.price_observers[symbol][period]) == 0:
            self.data_provider.unsubscribe(symbol)
            del(self.price_observers[symbol][period])

    def tick_update(self, symbol, tick):
        # we probably need to conflate prices to bake available to algorithms
        try:
            for conflationHandlers in self.price_observers[symbol].values():
                conflationHandlers.add_tick(tick)
        except KeyError as e:
            logging.error("Received data update for symbol we're not subscribed to (%s)" % (symbol,))

class PriceConflator(object):
    def __init__(self, symbol, period, callback = None):
        if not isinstance(period, datetime.timedelta):
            raise TypeError("period must be a timedelta")
        self.symbol = symbol
        self.period = period
        self.callback = callback
        self.period_starting_timestamp = None
        self.current_quote = None

    @staticmethod
    def round_datetime_to_period(timestamp, period):
        return timestamp - timestamp % period

    def add_tick(self, tick):
        grouping_period = self.period.total_seconds()

        if not self.current_quote:
            self.period_starting_timestamp = PriceConflator.round_datetime_to_period(tick.timestamp, grouping_period)
            self.current_quote = Quote(self.symbol, datetime.datetime.utcfromtimestamp(self.period_starting_timestamp), self.period, tick)
            return self.current_quote
        else:
            current_tick_timeblock = PriceConflator.round_datetime_to_period(tick.timestamp, grouping_period)
            if (current_tick_timeblock - self.period_starting_timestamp) < grouping_period:
                self.current_quote.add_tick(tick)
            else:
                if self.callback is not None:
                    self.callback(self.current_quote)
                t = self.period_starting_timestamp + grouping_period
                while current_tick_timeblock >= (t + grouping_period):
                        self.callback(Quote(self.symbol, datetime.datetime.utcfromtimestamp(t), self.period, Tick(self.period_starting_timestamp, self.current_quote.close, self.current_quote.close)))
                        t += grouping_period
                self.current_quote = Quote(self.symbol, datetime.datetime.utcfromtimestamp(t), self.period, tick)
                self.period_starting_timestamp = t
                return self.current_quote
        return None
