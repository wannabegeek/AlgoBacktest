import locale
import logging
from results.equity_curve import MatlibPlotResults


def display_results(container):
    totalPositions = len(list(filter(lambda x: not x.isOpen(), container.context.positions)))
    locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')

    if totalPositions == 0:
        print("=========================================================")
        print("Algo: %s" % (container.algo.identifier(),))
        print("No Positions taken")
    else:
        closed = list(map(lambda x: "\t%s%s  --> %.2fpts (%s)\x1B[;0m" % ("\x1B[;31m" if x.pointsDelta() < 0.0 else "\x1B[;32m", x, x.pointsDelta(), x.positionTime()), filter(lambda x: not x.isOpen(), container.context.positions)))
        open = list(map(lambda x: "\t%s" % (x), filter(lambda x: x.isOpen(), container.context.positions)))
        winning = list(filter(lambda x: x.pointsDelta() > 0.0, filter(lambda x: not x.isOpen(), container.context.positions)))

        print("=========================================================")
        print("Algo:             %s" % (container.algo.identifier(),))
        print("Winning Ratio:    %.2f%%" % ((len(winning)/totalPositions * 100),))
        print("Total Pts:        %.2f" % (sum([x.pointsDelta() for x in filter(lambda x: not x.isOpen(), container.context.positions)]), ))
        print("Starting Capital: %s" % (locale.currency(container.starting_capital, grouping=True),))
        print("Current Capital:  %s" % (locale.currency(container.context.working_capital, grouping=True),))
        print("Capital Change:  %s" % (locale.currency(container.context.working_capital, grouping=True),))
        print("---------------------------------------------------------")
        print("Completed:\n%s" % ("\n".join(closed),))
        print("Open:\n%s" % ("\n".join(open),))
