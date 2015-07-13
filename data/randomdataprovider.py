import datetime
import logging
from random import random
from data.data_provider import Provider
from market.price import Tick
from market.symbol import Symbol

base_price = 10.0
spread = 0.7

class RandomProvider(Provider):
    def __init__(self, symbol, iterations = 100, interval = datetime.timedelta(seconds=1)):
        self.symbol = symbol
        self.iterations = iterations
        self.interval = interval
        self.last_publish_time = datetime.datetime.now()

    def register(self, symbol):
        if not isinstance(symbol, Symbol):
            raise TypeError("symbol must be a Symbol object")
        self.symbol = symbol
        pass

    def loadHistoricalData(self, period):
        logging.debug("Loading historical data for the previous %s interval" % (period, ))
        pass

    def startPublishing(self, callback):
        for i in range(0, self.iterations):
            price = base_price + random() - (spread / 2.0)
            callback(self.symbol, Tick(self.last_publish_time, float(price), float(price + spread)))
            self.last_publish_time = self.last_publish_time + self.interval
