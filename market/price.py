from datetime import timedelta, datetime, timezone
import logging
import statistics
from market.market_data import MarketData, MarketDataPeriod


class Tick(object):
    """
    A single tick in the market, this contains just a bid, offer and volume
    Market depth isn't available in this framework yet
    """
    def __init__(self, timestamp, bid, offer, volume = 0):
        self.timestamp = timestamp
        self.bid = bid
        self.offer = offer
        self.volume = volume

    def spread(self):
        return self.offer - self.spread

    def midPrice(self):
        return statistics.mean([self.bid, self.offer])

    def __str__(self):
        return "%s: b:%s o:%s" % (self.timestamp, self.bid, self.offer)

    __repr__ = __str__

def roundDateTimeToPeriod(timestamp, period):
    roundTo = period.total_seconds()
    seconds = timestamp.replace(tzinfo=timezone.utc).timestamp() % roundTo
    return timestamp - timedelta(seconds=seconds)

class PriceConflator(object):
    def __init__(self, symbol, period, callback = None):
        if not isinstance(period, timedelta):
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
            if currentTickTimeBlock.timestamp() < (self.currentQuote.startTime + self.period).timestamp():
                self.currentQuote.addTick(tick)
            else:
                if self.callback is not None:
                    self.callback(self.currentQuote)
                t = self.currentQuote.startTime + self.period
                while currentTickTimeBlock.timestamp() >= (t + self.period).timestamp():
                        self.callback(Quote(self.symbol, t, self.period, Tick(self.currentQuote.startTime, self.currentQuote.close, self.currentQuote.close)))
                        t = t + self.period
                self.currentQuote = Quote(self.symbol, t, self.period, tick)
                return self.currentQuote
        return None


class Quote(object):
    """
    A single quote representaion. This is for conflated data, so it contains OHLC data.
    """

    def __init__(self, symbol, startTime, period, tick):
        self.symbol = symbol
        self.volume = None
        self.startTime = startTime
        self.period = period
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.ticks = 0
        self.lastTick = None
        self.addTick(tick)

    def addTick(self, tick):
        price = tick.midPrice()
        if self.open is None:
            self.open = price
        self.high = price if self.high is None else max(self.high, price)
        self.low = price if self.low is None else min(self.low, price)
        self.close = price
        self.lastTick = tick
        self.ticks = self.ticks + 1

    def __str__(self):
        return "{} -> {}: {:.6f} -> {:.6f} o:{:.6f} c:{:.6f}".format(self.startTime, self.startTime + self.period, self.low, self.high, self.open, self.close)
