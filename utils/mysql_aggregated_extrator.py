import logging
import pickle
from data.mysql_aggregateddata_provider import MySQLProvider
from data.mysql_symbol_provider import MySQLSymbolProvider
from market.market_data import MarketDataPeriod
from market.symbol import Symbol


class Extractor(object):

    def __init__(self):
        self.quotes = []

    def add_quote(self, quote):
        pickle.dump(quote, self.file_handle)

    def run(self):
        database = {'user': 'blackbox', 'database': 'blackbox', 'host': "localhost"}
        Symbol.setDataProvider(MySQLSymbolProvider(database))
        provider = MySQLProvider(database, Symbol.get('EURUSD:CUR'), MarketDataPeriod.DAY.total_seconds())

        self.file_handle = open(r"market_data_d1.pkl", "wb")
        provider.startPublishing(lambda symbol, quote: self.add_quote(quote))
        self.file_handle.close()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    e = Extractor()
    e.run()
