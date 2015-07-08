import datetime
import logging
from data.data_provider import Provider
from strategycontainer.price import Tick
from strategycontainer.symbol import Symbol


class CSVProvider(Provider):
    def __init__(self):
        Symbol.setDataProvider("1")
        self.symbol = None

    def register(self, symbol):
        self.symbol = symbol
        pass

    def loadHistoricalData(self, period):
        logging.debug("Loading historical data for the previous %s interval" % (period, ))
        pass

    def startPublishing(self, callback):
        tick = Tick(datetime.datetime.utcnow(), 10.1, 10.2)
        callback(self.symbol, tick)
