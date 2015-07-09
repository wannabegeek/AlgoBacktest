import logging
from algorithms.sample_algorithm import Algo
from data.csvtickdataprovider import CSVProvider
from strategycontainer.container import Container
from strategycontainer.position import Position


def printResults(context):

    logging.info("==========================================================")
    logging.info("Total Positions: %s" % (len(context.positions), ))
    logging.info("Positions still open: %s" % (len(list(context.getOpenPositions())), ))

    positions = filter(lambda x: x.exitReason == Position.ExitReason.TAKE_PROFIT, context.positions)
    totalPoints = sum([x.pointsDelta() for x in positions])
    logging.info("Total Points Gained: %s (from %s profit targets hit)" % (totalPoints, len(list(positions)) ))
    # positions = filter(lambda x: x.exitReason == Position.ExitReason.CLOSED, context.positions)

    positions = filter(lambda x: x.exitReason == Position.ExitReason.STOP_LOSS, context.positions)
    totalPoints = sum([x.pointsDelta() for x in positions])
    logging.info("Total Points Lost: %s (from %s stop loss targets hit)" % (totalPoints, len(list(positions)) ))


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    container = Container(Algo(), CSVProvider("/Users/tom/Downloads/HISTDATA_COM_ASCII_EURUSD_T201505/DAT_ASCII_EURUSD_T_201505-SHORT.csv"))
    container.start()

    printResults(container.context)
    logging.info("All done... shutting down")

if __name__ == '__main__':
    main()