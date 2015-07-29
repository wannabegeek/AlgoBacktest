import logging


def display_results(container):
    total_positions = len(list(filter(lambda x: not x.is_open(), container.context.positions)))

    if total_positions == 0:
        logging.info("========================")
        logging.info("Algo: %s" % (container.algo.identifier(),))
        logging.info("No Positions taken")
    else:
        closed = list(map(lambda x: "%s  --> %.2fpts (%s)" % (x, x.points_delta(), x.position_time()), filter(lambda x: not x.is_open(), container.context.positions)))
        open = list(map(lambda x: "%s" % (x), filter(lambda x: x.is_open(), container.context.positions)))
        winning = list(filter(lambda x: x.points_delta() > 0.0, filter(lambda x: not x.is_open(), container.context.positions)))

        logging.info("========================")
        logging.info("Algo:          %s" % (container.algo.identifier(),))
        logging.info("Winning Ratio: %.2f%%" % ((len(winning)/total_positions * 100),))
        logging.info("Total Pts:     %.2f" % (sum([x.points_delta() for x in filter(lambda x: not x.is_open(), container.context.positions)]), ))
        logging.info("------------------------")
        logging.info("Completed:\n%s" % ("\n".join(closed),))
        logging.info("Open:\n%s" % ("\n".join(open),))
