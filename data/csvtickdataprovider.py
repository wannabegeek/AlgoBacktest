import datetime
import logging
import time
import random
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
        now = datetime.datetime.utcnow()
        interval = datetime.timedelta(seconds=60)
        for i in range(1, 15):
            now = now + interval
            tick = Tick(now, 10.0 - random.random(), 10.0 + random.random())
            callback(self.symbol, tick)
            time.sleep(1)
