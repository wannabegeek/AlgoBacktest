import logging
import datetime
from algorithms.scalp_5m_pin_bar import Algo

from backtest.simulated_broker import Broker
from data.sqlitetickdataprovider import SQLiteProvider
from market.market_data import MarketData
from market.orderbook import OrderBook
from results.coloured_console import display_results
from strategy.container import Container
from market.symbol import Symbol

def main():
    Symbol.setDataProvider("")

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    venue_connection = Broker(SQLiteProvider(Symbol("EURUSD:CUR"), "../utils/test.store", startDate=datetime.datetime(2015, 6, 29)))

    order_book = OrderBook(venue_connection)
    market_data = MarketData(venue_connection)

    containers = []
    containers.append(Container(Algo(25, 10, 10), order_book, market_data))
    # containers.append(Container(Algo(15, 5, 10), order_book, market_data))
    # container.start()

    venue_connection.start()

    for container in containers:
        logging.info("==========================================================")
        display_results(container)

if __name__ == '__main__':
    main()
