import logging

from algorithms.sample_algorithm import Algo
from backtest.simulated_broker import Broker
from data.csvtickdataprovider import CSVProvider
from data.randomdataprovider import RandomProvider
from data.sqlitetickdataprovider import SQLiteProvider
from market.market_data import MarketData
from market.orderbook import OrderBook, BacktestOrderbook
from strategy.container import Container, MultiThreadedContainer
from market.position import Position
from market.symbol import Symbol


def printResults(context):

    logging.info("==========================================================")
    logging.info("Total Positions: %s" % (len(context.positions), ))
    logging.info("Positions still open: %s" % (len(list(context.getOpenPositions())), ))

    positions = filter(lambda x: x.exitReason == Position.PositionStatus.TAKE_PROFIT, context.positions)
    totalPoints = sum([x.pointsDelta() for x in positions])
    logging.info("Total Points Gained: %s (from %s profit targets hit)" % (totalPoints, len(list(positions)) ))
    # positions = filter(lambda x: x.exitReason == Position.ExitReason.CLOSED, context.positions)

    positions = filter(lambda x: x.exitReason == Position.PositionStatus.STOP_LOSS, context.positions)
    totalPoints = sum([x.pointsDelta() for x in positions])
    logging.info("Total Points Lost: %s (from %s stop loss targets hit)" % (totalPoints, len(list(positions)) ))


def main():
    Symbol.setDataProvider("")

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    # venue_connection = Broker(RandomProvider(Symbol("EURUSD:CUR"), 10000))
    venue_connection = Broker(SQLiteProvider(Symbol("EURUSD:CUR"), "../utils/test.store"))
    # venue_connection = Broker(CSVProvider(Symbol("EURUSD:CUR"), "/Users/tom/Downloads/HISTDATA_COM_ASCII_EURUSD_T201506/DAT_ASCII_EURUSD_T_201506-SHORT.csv"))

    order_book = BacktestOrderbook(venue_connection)
    market_data = MarketData(venue_connection)

    container = Container(Algo(), order_book, market_data)
    # container.start()

    venue_connection.start()

    printResults(container.context)
    logging.info("All done... shutting down")

    print(order_book)

if __name__ == '__main__':
    main()