import logging
from algorithms.scalp_5m_pin_bar import Algo

from backtest.simulated_broker import Broker
from data.sqlitetickdataprovider import SQLiteProvider
from market.market_data import MarketData
from market.orderbook import OrderBook, BacktestOrderbook
from strategy.container import Container, MultiThreadedContainer
from market.symbol import Symbol

def main():
    Symbol.setDataProvider("")

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    venue_connection = Broker(SQLiteProvider(Symbol("EURUSD:CUR"), "../utils/test.store"))

    order_book = BacktestOrderbook(venue_connection)
    market_data = MarketData(venue_connection)

    # container = Container(Algo(25, 10, 10), order_book, market_data)
    container = Container(Algo(15, 5, 10), order_book, market_data)
    # container.start()

    venue_connection.start()

    logging.info("==========================================================")
    for line in str(container).splitlines():
        logging.info(line)

if __name__ == '__main__':
    main()
