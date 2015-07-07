from datetime import timedelta, datetime, timezone
import statistics

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
            self.currentQuote = Quote(roundDateTimeToPeriod(tick.timestamp, self.period), self.period, tick)
        else:
            currentTickTimeBlock = roundDateTimeToPeriod(tick.timestamp, self.period)
            if currentTickTimeBlock.timestamp() < (self.currentQuote.startTime + self.period).timestamp():
                self.currentQuote.addTick(tick)
            else:
                if self.callback is not None:
                    self.callback(self.currentQuote)
                t = self.currentQuote.startTime + self.period
                while currentTickTimeBlock.timestamp() >= (t + self.period).timestamp():
                        self.callback(Quote(t, self.period, Tick(self.currentQuote.startTime, self.currentQuote.close, self.currentQuote.close)))
                        t = t + self.period
                self.currentQuote = Quote(t, self.period, tick)


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

    def __str__(self):
        return "{:.4f} -> {:.4f} o:{:.4f} c:{:.4f}".format(self.low, self.high, self.open, self.close)