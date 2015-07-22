import datetime
import logging
import csv
import pytz

from data.data_provider import Provider
from market.price import Tick
from market.symbol import Symbol


class CSVProvider(Provider):

    def __init__(self, symbol, filename):
        self.symbol = symbol
        self.reader = csv.reader(open(filename, 'r'))
        self.tz = pytz.timezone('America/New_York')

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
            ts = self.tz.localize(ts)
            callback(self.symbol, Tick(ts.astimezone(pytz.utc), float(bid), float(ask)))

    def setProgressCallback(self, callback):
        raise NotImplementedError("setProgressCallback isn't implemented for this Provider instance")
