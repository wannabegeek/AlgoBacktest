import logging

from algorithms.sample_algorithm import Algo
from backtest.simulated_broker import Broker
from data.csvtickdataprovider import CSVProvider
from strategy.container import Container
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
    order_manager = Broker(CSVProvider(Symbol("FTSE:IDX"), "/Users/tom/Downloads/HISTDATA_COM_ASCII_EURUSD_T201506/DAT_ASCII_EURUSD_T_201506.csv"))

    container = Container(Algo(), order_manager, order_manager)

    order_manager.start()

    printResults(container.context)
    logging.info("All done... shutting down")

if __name__ == '__main__':
    main()