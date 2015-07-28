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
        self.quotes.append(quote)

    def run(self):
        database = {'user': 'blackbox', 'database': 'blackbox', 'host': "192.168.0.8"}
        Symbol.setDataProvider(MySQLSymbolProvider(database))
        provider = MySQLProvider(database, Symbol.get('EURUSD:CUR'), MarketDataPeriod.HOUR_1)

        provider.startPublishing(lambda symbol, quote: self.add_quote(quote))

        with open(r"market_data_h1.pkl", "wb") as output_file:
            pickle.dump(self.quotes, output_file)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    e = Extractor()
    e.run()