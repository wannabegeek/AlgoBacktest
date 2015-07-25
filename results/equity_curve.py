import datetime
import matplotlib
#this needs to be dne for headless boxes (& needs to be done before any other imports)
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

matplotlib.rcParams.update({'font.size': 9})

# pound = u'\N{pound sign}'
pound = '$'

class MatlibPlotResults(object):

    def __init__(self):
        self.capital = 0

    def calculate_capital(self, change):
        self.capital += change
        return self.capital

    def display(self, container, io=False):
        #
        # Plot a graph
        #
        self.capital = container.starting_capital

        closed_positions = sorted(filter(lambda x: not x.isOpen(), container.context.positions), key=lambda x: x.exitTick.timestamp)
        date = [mdates.date2num(datetime.datetime.utcfromtimestamp(o.exitTick.timestamp)) for o in closed_positions]
        algorithm_performance = [self.calculate_capital(float(o.equity())) for o in closed_positions]

        date.insert(0, mdates.date2num(container.context.startTime))
        algorithm_performance.insert(0, container.starting_capital)

        mondays = mdates.WeekdayLocator(mdates.MONDAY)        # major ticks on the mondays
        alldays = mdates.DayLocator()              # minor ticks on the days
        weekFormatter = mdates.DateFormatter('%b %d %Y')  # e.g., Jan 12
        dayFormatter = mdates.DateFormatter('%d')      # e.g., 12

        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2)
        ax.xaxis.set_major_locator(mondays)
        ax.xaxis.set_minor_locator(alldays)
        ax.xaxis.set_major_formatter(weekFormatter)
        #ax.xaxis.set_minor_formatter(dayFormatter)

        ax.plot(date, algorithm_performance, linewidth=1)

        ax.xaxis_date()
        ax.autoscale_view()
        plt.setp(plt.gca().get_xticklabels(), rotation=90, horizontalalignment='right')

        fig.set_size_inches(14.0, 5.0)

        if io is not None:
            plt.savefig(io, bbox_inches='tight', format="png", dpi=72)
        else:
            plt.show()
