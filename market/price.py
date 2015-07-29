import datetime


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

    def mid_price(self):
        return (self.bid + self.offer) / 2.0

    def __str__(self):
        return "%s: b:%s o:%s" % (datetime.datetime.utcfromtimestamp(self.timestamp), self.bid, self.offer)

    __repr__ = __str__

class Quote(object):
    """
    A single quote representaion. This is for conflated data, so it contains OHLC data.
    """

    def __init__(self, symbol, start_time, period, tick):
        self.symbol = symbol
        self.volume = None
        self.start_time = start_time
        self.period = period
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.ticks = 0
        self.last_tick = None
        self.add_tick(tick)

    def add_tick(self, tick):
        price = tick.mid_price()
        if self.last_tick is None:
            self.open = price
            self.high = price
            self.low = price
            self.close = price
        else:
            self.high = max(self.high, price)
            self.low = min(self.low, price)
            self.close = price
        self.last_tick = tick
        self.ticks += 1

    def __str__(self):
        return "{} -> {}: {:.6f} -> {:.6f} o:{:.6f} c:{:.6f} ({:d})".format(self.start_time, self.start_time + self.period, self.low, self.high, self.open, self.close, self.ticks)
