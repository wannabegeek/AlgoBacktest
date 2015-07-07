from datetime import timedelta, datetime, timezone
import statistics

class Tick(object):
    def __init__(self, timestamp, bid, offer, volume = 0):
        self.timestamp = timestamp
        self.bid = bid
        self.offer = offer
        self.volume = volume

    def spread(self):
        return self.offer - self.spread

    def midPrice(self):
        return statistics.mean([self.bid, self.offer])


class PriceConflator(object):
    def __init__(self, symbol, period, callback = None):
        if not isinstance(period, timedelta):
            raise TypeError("period must be a timedelta")
        self.symbol = symbol
        self.period = period
        self.callback = callback
        self.periodStartingTimestamp = None
        self.currentQuote = None

    @classmethod
    def _roundDateTimeToPeriod(cls, timestamp, period):
        roundTo = period.total_seconds()
        seconds = timestamp.replace(tzinfo=timezone.utc).timestamp() % roundTo 
        return timestamp - timedelta(seconds=seconds)

    def addTick(self, tick):
        if not self.currentQuote:
            self.periodStartingTimestamp = tick.timestamp
            self.currentQuote = Quote(self._roundDateTimeToPeriod(tick.timestamp, self.period), self.period, tick)
        else:
            currentTickTimeBlock = self._roundDateTimeToPeriod(tick.timestamp, self.period)
            print("tick:%s block:%s" % (tick.timestamp, currentTickTimeBlock))
            print("quoteTime:%s " % (self.currentQuote.startTime, ))
            if self.currentQuote.startTime + self.period < currentTickTimeBlock:
                self.currentQuote.addTick(tick)
            else:
                if self.callback is not None:
                    self.callback(self.currentQuote)
                self.currentQuote = Quote(self.currentQuote.startTime + self.period, self.period, tick)


class Quote(object):
    """
    A single quote representaion. This is for conflated data, so it contains OHLC data.
    """

    def __init__(self, startTime, period, tick):
        self.volume = None
        self.startTime = startTime
        self.period = period
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.addTick(tick)

    def addTick(self, tick):
        price = tick.midPrice()
        if self.open is None:
            self.open = price
        self.high = price if self.high is None else max(self.high, price)
        self.low = price if self.low is None else min(self.low, price)
        self.close = price
        self.timestamp = tick.timestamp

    def setWithDictionary(self, values, keys):
        (self.timestamp, self.high, self.low, self.volume, self.close, self.open) = [values.get(k) for k in keys]

    def __str__(self):
        return "{} - {}: {:.4f} -> {:.4f} o:{:.4f} c:{:.4f}".format(self.symbol.name, self.timestamp, self.low, self.high, self.open, self.close)
