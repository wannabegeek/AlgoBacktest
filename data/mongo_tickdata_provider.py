import datetime
import logging
from data.interfaces.data_provider import Provider
from pymongo import MongoClient
from market.price import Tick
from market.symbol import Symbol


class MongoProvider(Provider):
    def __init__(self, credentials, symbol, start_date=None, end_date=None, multithreaded=False):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.multithreaded = multithreaded
        self._db_connection = MongoClient('192.168.0.8', 27017)
        self.collection = self._db_connection.test
        self.progress_callback = None
        self.progress_count = 0
        self._expected_result_count = None
        self._callback_interval = 0
        self.query = {"symbol_id" : self.symbol.identifier}
        ts = {}
        if start_date is not None:
            ts["$gt"] = self.start_date.timestamp() * 1000
        if end_date is not None:
            ts["$lt"] = self.end_date.timestamp() * 1000

        if len(ts) > 0:
            self.query["timestamp"] = ts

    @property
    def expected_result_count(self):
        if self._expected_result_count is None:
            self._expected_result_count = self.collection.tick_data.find(self.query).count()
            self._callback_interval = int(self._expected_result_count / 100.0)
        return self._expected_result_count

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def register(self, symbol):
        if not isinstance(symbol, Symbol):
            raise TypeError("symbol must be a Symbol object")
        self.symbol = symbol

    def load_historical_data(self, period):
        logging.debug("Loading historical data for the previous %s interval" % (period, ))

    def start_publishing(self, callback):
            for tick in self.collection.tick_data.find(self.query).sort("timestamp"):
                callback(self.symbol, Tick(tick['timestamp'] / 1000, tick['bid'], tick['offer']))
                self.progress_count += 1
                if self.progress_callback is not None:
                    if self.progress_count % self._callback_interval == 0:
                        self.progress_callback(self.progress_count)
