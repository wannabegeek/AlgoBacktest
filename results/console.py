import logging


def display_results(container):
    totalPositions = len(list(filter(lambda x: not x.isOpen(), container.context.positions)))

    if totalPositions == 0:
        logging.info("========================")
        logging.info("Algo: %s" % (container.algo.identifier(),))
        logging.info("No Positions taken")
    else:
        closed = list(map(lambda x: "%s  --> %.2fpts (%s)" % (x, x.pointsDelta(), x.positionTime()), filter(lambda x: not x.isOpen(), container.context.positions)))
        open = list(map(lambda x: "%s" % (x), filter(lambda x: x.isOpen(), container.context.positions)))
        winning = list(filter(lambda x: x.pointsDelta() > 0.0, filter(lambda x: not x.isOpen(), container.context.positions)))

        logging.info("========================")
        logging.info("Algo:          %s" % (container.algo.identifier(),))
        logging.info("Winning Ratio: %.2f%%" % ((len(winning)/totalPositions * 100),))
        logging.info("Total Pts:     %.2f" % (sum([x.pointsDelta() for x in filter(lambda x: not x.isOpen(), container.context.positions)]), ))
        logging.info("------------------------")
        logging.info("Completed:\n%s" % ("\n".join(closed),))
        logging.info("Open:\n%s" % ("\n".join(open),))
