import datetime
import logging
import csv
from data.data_provider import Provider
from strategycontainer.price import Tick
from strategycontainer.symbol import Symbol


class CSVProvider(Provider):
    def __init__(self, filename):
        self.symbol = None
        self.reader = csv.reader(open(filename, 'r'))

    def register(self, symbol):
        if not isinstance(symbol, Symbol):
            raise TypeError("symbol must be a Symbol object")
        self.symbol = symbol
        pass

    def loadHistoricalData(self, period):
        logging.debug("Loading historical data for the previous %s interval" % (period, ))
        pass

    def startPublishing(self, callback):
        for timestamp, bid, ask, volume in self.reader:
            ts = datetime.datetime.strptime(timestamp, "%Y%m%d %H%M%S%f")
            callback(self.symbol, Tick(ts, float(bid), float(ask)))
        # now = datetime.datetime.utcnow()
        # interval = datetime.timedelta(seconds=60)
        # for i in range(1, 150):
        #     now = now + interval
        #     tick = Tick(now, 10.0 - random.random(), 10.0 + random.random())
        #     callback(self.symbol, tick)
        #     time.sleep(0.1)
