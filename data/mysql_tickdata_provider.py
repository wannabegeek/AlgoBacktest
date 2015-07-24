import datetime
import logging
import mysql.connector

from data.interfaces.data_provider import Provider
from market.price import Tick
from market.symbol import Symbol

def ResultIter(cursor, arraysize=1000):
    'An iterator that uses fetchmany to keep memory usage down'
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result


class MySQLProvider(Provider):
    def __init__(self, symbol, startDate=datetime.datetime(datetime.MINYEAR, 1, 1), endDate=datetime.datetime(datetime.MAXYEAR, 1, 1)):
        self.symbol = symbol
        self.startDate = startDate
        self.endDate = endDate
        self._db_connection = mysql.connector.connect(user='blackbox', database='blackbox', host="localhost")
        self.cursor = self._db_connection.cursor()
        self.progress_callback = None
        self.progress_count = 0

        self.cursor.execute("SELECT count(*) FROM tick_data WHERE symbol_id = %s AND timestamp BETWEEN %s and %s", (self.symbol.identifier, self.startDate, self.endDate))
        for result in self.cursor:
            self.expected_result_count = result[0]

        self.callback_interval = int(self.expected_result_count / 100.0)

    def setProgressCallback(self, callback):
        self.progress_callback = callback

    def register(self, symbol):
        if not isinstance(symbol, Symbol):
            raise TypeError("symbol must be a Symbol object")
        self.symbol = symbol

    def loadHistoricalData(self, period):
        logging.debug("Loading historical data for the previous %s interval" % (period, ))

    def startPublishing(self, callback):
        self.cursor.execute("SELECT timestamp, bid, offer FROM tick_data WHERE symbol_id = %s AND timestamp BETWEEN %s and %s ORDER BY timestamp", (self.symbol.identifier, self.startDate, self.endDate))
        for tick in ResultIter(self.cursor):
            callback(self.symbol, Tick(tick[0], tick[1], tick[2]))
            self.progress_count += 1
            if self.progress_callback is not None:
                if self.progress_count % self.callback_interval == 0:
                    self.progress_callback(self.progress_count)
