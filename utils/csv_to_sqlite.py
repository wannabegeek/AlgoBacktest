import sqlite3
from data.csvtickdataprovider import CSVProvider
from market.symbol import Symbol

class Handler(object):
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)

        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA synchronous = OFF")
        self.cursor.execute("PRAGMA journal_mode = OFF")

        self.cursor.execute("CREATE TABLE IF NOT EXISTS tick_data("
                               "symbol varchar(64) NOT NULL,"
                               "timestamp datetime NOT NULL,"
                               "bid NUMBER NOT NULL,"
                               "offer NUMBER NOT NULL)")

        data = CSVProvider(Symbol("EURUSD:CUR"), "c:\DAT_ASCII_EURUSD_T_201505-SHORT.csv")
        data.startPublishing(self.tickHandler)

    def tickHandler(self, symbol, tick):
        self.cursor.execute("INSERT INTO tick_data(symbol, timestamp, bid, offer) VALUES(?, ?, ?, ?)", (symbol.identifier, tick.timestamp, tick.bid, tick.offer))
        self.conn.commit()

if __name__ == '__main__':
    Symbol.setDataProvider("")
    h = Handler("test.store")
