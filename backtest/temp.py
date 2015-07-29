import logging
from algorithms.scalp_5m_pin_bar import Algo

from backtest.simulated_broker import Broker
from market.market_data import MarketData
from market.orderbook import OrderBook
from results.email import display_results
from strategy.container import Container
from utils.config import Config
from utils.progress_bar import ProgressBar


def main():

    config = Config("config.conf")

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    data_provider = config.data_provider

    venue_connection = Broker(data_provider)

    order_book = OrderBook(venue_connection)
    market_data = MarketData(venue_connection)

    containers = []
#    containers.append(Container(Algo(25, 10, 10), 10000, order_book, market_data))
#   containers.append(Container(Algo(15, 5, 10), 10000, order_book, market_data))
    containers.append(Container(Algo(15, 50, 100), 100000, order_book, market_data))
    # container.start()

    progress_bar = ProgressBar(data_provider.expected_result_count, label='Backtest')
    data_provider.set_progress_callback(lambda x: progress_bar.set(x))

    venue_connection.start()
    progress_bar.complete()

    for container in containers:
        display_results(container)

if __name__ == '__main__':
    main()
