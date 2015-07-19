import datetime
import logging
import sqlite3

from data.data_provider import Provider
from market.price import Tick
from market.symbol import Symbol


class SQLiteProvider(Provider):
    def __init__(self, symbol, filename, startDate=datetime.datetime(datetime.MINYEAR, 1, 1), endDate=datetime.datetime(datetime.MAXYEAR, 1, 1)):
        self.symbol = symbol
        self.startDate = startDate
        self.endDate = endDate
        self.conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.conn.cursor()

    def register(self, symbol):
        if not isinstance(symbol, Symbol):
            raise TypeError("symbol must be a Symbol object")
        self.symbol = symbol
        pass

    def loadHistoricalData(self, period):
        logging.debug("Loading historical data for the previous %s interval" % (period, ))
        pass

    def startPublishing(self, callback):
        self.cursor.execute("SELECT timestamp, bid, offer FROM tick_data WHERE symbol = ? AND timestamp >= ? and timestamp <= ? ORDER BY timestamp", (self.symbol.identifier, self.startDate, self.endDate))
        for tick in self.cursor:
            callback(self.symbol, Tick(tick[0], tick[1], tick[2]))
