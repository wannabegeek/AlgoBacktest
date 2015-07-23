import logging
import datetime
from algorithms.scalp_5m_pin_bar import Algo

from backtest.simulated_broker import Broker
from data.mysql_symbol_provider import MySQLSymbolProvider
from data.sqlite_tickdata_provider import SQLiteProvider
from market.market_data import MarketData
from market.orderbook import OrderBook
from results.email import display_results
from strategy.container import Container
from market.symbol import Symbol
from utils.progress_bar import ProgressBar


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    Symbol.setDataProvider(MySQLSymbolProvider())

    data_provider = SQLiteProvider(Symbol.get("EURUSD:CUR"), "../utils/test.store", startDate=datetime.datetime(2015, 6, 29))
    venue_connection = Broker(data_provider)

    order_book = OrderBook(venue_connection)
    market_data = MarketData(venue_connection)

    containers = []
    containers.append(Container(Algo(25, 10, 10), 10000, order_book, market_data))
    containers.append(Container(Algo(15, 5, 10), 10000, order_book, market_data))
    containers.append(Container(Algo(15, 10, 5), 10000, order_book, market_data))
    # container.start()

    progress_bar = ProgressBar(data_provider.expected_result_count)
    data_provider.setProgressCallback(lambda x: progress_bar.set(x))

    venue_connection.start()
    progress_bar.complete()

    for container in containers:
        display_results(container)

if __name__ == '__main__':
    main()
