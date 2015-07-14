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

    def __str__(self):
        return "%s: b:%s o:%s" % (self.timestamp, self.bid, self.offer)

    __repr__ = __str__

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
