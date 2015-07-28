import datetime
import logging
import multiprocessing
import mysql.connector
from multiprocessing import Process

from data.interfaces.data_provider import Provider
from market.price import Tick, Quote
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
    def __init__(self, credentials, symbol, period, startDate=datetime.datetime.fromtimestamp(0), endDate=datetime.datetime.max, multithreaded=False):
        self.symbol = symbol
        self.period = period
        self.startDate = startDate
        self.endDate = endDate
        self.multithreaded = multithreaded
        self._db_connection = mysql.connector.connect(**credentials)
        self.cursor = self._db_connection.cursor()
        self.progress_callback = None
        self.progress_count = 0
        self._expected_result_count = None
        self._callback_interval = 0

    @property
    def expected_result_count(self):
        raise NotImplementedError("Not implemented")

    def setProgressCallback(self, callback):
        self.progress_callback = callback

    def register(self, symbol):
        if not isinstance(symbol, Symbol):
            raise TypeError("symbol must be a Symbol object")
        self.symbol = symbol

    def loadHistoricalData(self, period):
        logging.debug("Loading historical data for the previous %s interval" % (period, ))

    def getTickData(self, queue):
        # self._db_connection = mysql.connector.connect(user='blackbox', database='blackbox', host="192.168.0.8")
        cursor = self._db_connection.cursor()
        cursor.callproc('aggregated_data', [self.symbol.identifier, self.period, self.startDate.timestamp(), self.endDate.timestamp() ])
        for tick in self.cursor.stored_results():
            quote = Quote(self.symbol, tick[0], self.period, Tick(tick[0], tick[1], tick[1]))  # open
            quote.addTick(Tick(tick[0], tick[2], tick[2]))  # high
            quote.addTick(Tick(tick[0], tick[3], tick[3]))  # low
            quote.addTick(Tick(tick[0], tick[4], tick[4]))  # close
            queue.put(quote)
        queue.put(None)


    def startPublishing(self, callback):
        if self.multithreaded is True:
            queue = multiprocessing.Queue()

            p = Process(target=self.getTickData, args=(queue,))
            p.start()

            for quote in iter(queue.get, None):
                callback(self.symbol, quote)
                self.progress_count += 1
                if self.progress_callback is not None:
                    if self.progress_count % self._callback_interval == 0:
                        self.progress_callback(self.progress_count)
        else:
            st = self.startDate.timestamp()
            en = self.endDate.timestamp()
            self.cursor.callproc('aggregated_data', [self.symbol.identifier, self.period, self.startDate.timestamp(), self.endDate.timestamp() ])
            for results in self.cursor.stored_results():
                for tick in ResultIter(results):
                    quote = Quote(self.symbol, tick[0], self.period, Tick(tick[0], tick[1], tick[1]))  # open
                    quote.addTick(Tick(tick[0], tick[2], tick[2]))  # high
                    quote.addTick(Tick(tick[0], tick[3], tick[3]))  # low
                    quote.addTick(Tick(tick[0], tick[4], tick[4]))  # close
                    callback(self.symbol, quote)
                    self.progress_count += 1
                    if self.progress_callback is not None:
                        if self.progress_count % self._callback_interval == 0:
                            self.progress_callback(self.progress_count)

