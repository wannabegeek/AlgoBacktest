import argparse
import logging
from algorithms.naked_big_shadow import NakedBigShadow
from algorithms.scalp_5m_pin_bar import Algo
from backtest.backtest_orderbook_persist import BacktestOrderbookPersist

from backtest.simulated_broker import Broker
from market.market_data import MarketData
from market.orderbook import OrderBook
from results.email import display_results
from strategy.container import Container
from utils.config import Config
from utils.progress_bar import ProgressBar


def main():

    parser = argparse.ArgumentParser(description='Backtest an algorithm.')
    # parser.add_argument("-a", "--algo", dest="algo", required=True, help="algorithm identifier")
    parser.add_argument("-l", "--log-level", dest="log_level", choices=['DEBUG', 'INFO', 'WARN'], default="INFO", help="logging level")
    parser.add_argument("-p", "--show-progress", dest="show_progress", action='store_true', help="log progress")

    global args
    args = parser.parse_args()

    level = logging.INFO
    if args.log_level == 'DEBUG':
        level = logging.DEBUG
    elif args.log_level == 'INFO':
        level = logging.INFO
    elif args.log_level == 'WARN':
        level = logging.WARN
    logging.basicConfig(level=level)

    config = Config("config.conf")

    data_provider = config.data_provider
    venue_connection = Broker(data_provider)

    orderbook_persist = BacktestOrderbookPersist()
    order_book = OrderBook(venue_connection, orderbook_persist)
    market_data = MarketData(venue_connection)

    containers = []
#    containers.append(Container(Algo(25, 10, 10), 10000, order_book, market_data))
    containers.append(Container(NakedBigShadow(8, 20, 100), 10000, order_book, market_data))
    # containers.append(Container(Algo(15, 50, 100), 100000, order_book, market_data))

    if args.show_progress is True:
        progress_bar = ProgressBar(data_provider.expected_result_count, label='Backtest')
        data_provider.set_progress_callback(lambda x: progress_bar.set(x))
        venue_connection.start()
        progress_bar.complete()
    else:
        venue_connection.start()

    for container in containers:
        display_results(container)

if __name__ == '__main__':
    main()
