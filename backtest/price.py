from datetime import timedelta

class Tick(object):
    def __init__(self, timestamp, bid, offer, volume = 0):
        self.timestamp = timestamp
        self.bid = bid
        self.offer = offer
        self.volume = volume

    def spread(self):
        return self.offer - self.spread

    def midPrice(self):
        return avg(self.bid, self.offer)


class PriceConflator(object):
    def __init__(self, period, callback = None):
        if not isinstance(period, timedelta):
            raise TypeError("period must be a timedelta")
        self.period = period
        self.callback = callback
        self.currentQuote = Quote()

    def addTick(self, tick):
        self.currentQuote.addTick(tick)
        if we go to next period:
            self.callback(self.currentQuote)
            self.currentQuote = Quote()

class Quote(object):
    """
    A single quote representaion. This is for conflated data, so it contains OHLC data.
    """
    symbol = None
    timestamp = None
    open = None
    high = None
    low = None
    close = None
    volume = None

    data = {}

    def __init__(self, symbol):
        self.symbol = symbol

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
