import logging
import sqlite3
from data.csvtickdataprovider import CSVProvider
from market.symbol import Symbol

class Handler(object):
    def __init__(self, filename):
        self.pending = []
        self.totalTicks = 0
        self.conn = sqlite3.connect(filename)

        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA synchronous = OFF")
        self.cursor.execute("PRAGMA journal_mode = OFF")

        self.cursor.execute("CREATE TABLE IF NOT EXISTS tick_data("
                               "symbol varchar(64) NOT NULL,"
                               "timestamp timestamp NOT NULL,"
                               "bid NUMBER NOT NULL,"
                               "offer NUMBER NOT NULL)")

        data = CSVProvider(Symbol("EURUSD:CUR"), "/Users/tom/Downloads/HISTDATA_COM_ASCII_EURUSD_T201506/DAT_ASCII_EURUSD_T_201506.csv")
        data.startPublishing(self.tickHandler)

    def tickHandler(self, symbol, tick):
        self.pending.append((symbol.identifier, tick.timestamp, tick.bid, tick.offer))
        if len(self.pending) >= 10000:
            self.cursor.executemany("INSERT INTO tick_data(symbol, timestamp, bid, offer) VALUES(?, ?, ?, ?)", self.pending)
            self.totalTicks += len(self.pending)
            self.pending.clear()
            self.conn.commit()
            logging.debug("Commited %s" % (self.totalTicks,))

if __name__ == '__main__':
    Symbol.setDataProvider("")

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    h = Handler("test.store")
