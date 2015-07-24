from datetime import datetime, timedelta
import logging

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.finance import candlestick
import matplotlib
import pylab

matplotlib.rcParams.update({'font.size': 9})


# pound = u'\N{pound sign}'
pound = '$'

class MatlibPlotResults(object):

    def display(self, context):
        # work out the performance vs benchmark
        # performance = self.calculatePerformance(context)

        # algoClosePrices = [x[2] for x in performance][1:]
        # filter out all '0' close prices - we assume those are invalid data
        # algoClosePrices = filter(lambda a: a != 0, algoClosePrices)

        #
        # Plot a graph
        #

        closed_positions = list(filter(lambda x: not x.isOpen(), context.positions))
        date = [mdates.date2num(o.exitTick.timestamp) for o in closed_positions]
        # closep = [float(o[1]) for o in performance]
        algorithm_performance = [float(o.pointsDelta()) for o in closed_positions]
        # volume = [float(o[3]) for o in performance]

        # 'fig' is used for exporting the graph as an image
        fig = plt.figure(figsize=(18, 6), dpi=80, facecolor='#ffffff')

        # ax1 = plt.subplot2grid((6, 4), (1, 0), rowspan=4, colspan=4, axisbg='#ffffff')
        # candlestick(ax1, newAr[-SP:], width=.6, colorup='#53c156', colordown='#ff1717')
        # ax1.plot(date, closep, '#AA0000', label="Benchmark", linewidth=1.0)

        # Label1 = str(MA1) + ' EMA'
        # Label2 = str(MA2) + ' EMA'
        #
        # ax1.plot(date[-SP:], Av1[-SP:], '#e1edf9', label=Label1, linewidth=1.5)
        # ax1.plot(date[-SP:], Av2[-SP:], '#4ee6fd', label=Label2, linewidth=1.5)
        # ax1.plot(date, algorithmPerformance, '#0000AA', label="Algorithm", linewidth=1)

        longColor = '#386d13'
        shortColor = '#8f2020'

        # for position in context.closedPositions:
        #     directionColor = longColor if position.direction == PositionDirection.LONG else shortColor
        #     ax1.axvspan(mdates.date2num(position.entryQuote.timestamp),
        #                 mdates.date2num(position.exitQuote.timestamp), alpha=0.2, color=directionColor)

        # for position in context.openPositions:
        #     directionColor = longColor if position.direction == PositionDirection.LONG else shortColor
        #     ax1.axvspan(mdates.date2num(position.entryQuote.timestamp),
        #                 mdates.date2num(performance[-1][0]), alpha=0.6, color=directionColor)


        # ax1.grid(True, color='#000000')
        # ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        # ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # ax1.yaxis.label.set_color("#000000")
        # ax1.spines['bottom'].set_color("#5998ff")
        # ax1.spines['top'].set_color("#5998ff")
        # ax1.spines['left'].set_color("#5998ff")
        # ax1.spines['right'].set_color("#5998ff")
        # ax1.tick_params(axis='y', colors='#000000')
        # plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
        # ax1.tick_params(axis='x', colors='#000000')
        # plt.ylabel('Algorithm Performance')
        #
        # maLeg = plt.legend(loc=9, ncol=2, prop={'size': 7}, fancybox=True, borderaxespad=0.)
        # maLeg.get_frame().set_alpha(0.4)
        # textEd = pylab.gca().get_legend().get_texts()
        # pylab.setp(textEd[0:5], color='#000000')

        volumeMin = 0

        ax0 = plt.subplot2grid((6, 4), (0, 0), sharex=ax1, rowspan=1, colspan=4, axisbg='#ffffff')

        rsiCol = '#999999'
        posCol = '#386d13'
        negCol = '#8f2020'

        ax0.plot(date, algorithm_performance, rsiCol, linewidth=1)
        ax0.axhline(70, color=negCol)
        ax0.axhline(30, color=posCol)
        ax0.fill_between(date, rsi, 70, where=(rsi >= 70), facecolor=negCol, edgecolor=negCol, alpha=0.5)
        ax0.fill_between(date, rsi, 30, where=(rsi <= 30), facecolor=posCol, edgecolor=posCol, alpha=0.5)
        ax0.set_yticks([30, 70])
        ax0.yaxis.label.set_color("#000000")
        ax0.spines['bottom'].set_color("#5998ff")
        ax0.spines['top'].set_color("#5998ff")
        ax0.spines['left'].set_color("#5998ff")
        ax0.spines['right'].set_color("#5998ff")
        ax0.tick_params(axis='y', colors='#000000')
        ax0.tick_params(axis='x', colors='#000000')
        plt.ylabel('Performance')

        # ax1v = ax1.twinx()
        # ax1v.fill_between(date, volumeMin, volume, facecolor='#dddddd', alpha=.5)
        # ax1v.axes.yaxis.set_ticklabels([])
        # ax1v.grid(False)
        # ax1v.set_ylim(0, 3 * max(volume))
        # ax1v.spines['bottom'].set_color("#5998ff")
        # ax1v.spines['top'].set_color("#5998ff")
        # ax1v.spines['left'].set_color("#5998ff")
        # ax1v.spines['right'].set_color("#5998ff")
        # ax1v.tick_params(axis='x', colors='#000000')
        # ax1v.tick_params(axis='y', colors='#000000')
        #
        # if hasCustomData == True:
        #     ax2 = plt.subplot2grid((6, 4), (5, 0), sharex=ax1, rowspan=1, colspan=4, axisbg='#ffffff')
        #     # START NEW INDICATOR CODE #
        #
        #     colors = ['#AA0000', '#00AA00', '#0000AA']
        #     index = 0
        #     for customDataKey in context.custom_data:
        #         data = [self.customDataAtTime(context, customDataKey, o[0]) for o in performance]
        #         # data = [float(o) for o in context.custom_data[customDataKey]]
        #         ax2.plot(date, data, colors[index], label=customDataKey, linewidth=1)
        #         index+=1
        #
        #     # ax2.set_ylim(0, 1.5 * max(runningCapital))
        #
        #     # END NEW INDICATOR CODE #
        #
        #     plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
        #     ax2.spines['bottom'].set_color("#5998ff")
        #     ax2.spines['top'].set_color("#5998ff")
        #     ax2.spines['left'].set_color("#5998ff")
        #     ax2.spines['right'].set_color("#5998ff")
        #     ax2.tick_params(axis='x', colors='#000000')
        #     ax2.tick_params(axis='y', colors='#000000')
        #     plt.ylabel('Custom Data')
        #     ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))
        #
        #     for label in ax2.xaxis.get_ticklabels():
        #         label.set_rotation(45)

        plt.suptitle("Backtest Algo".upper(), color='#000000')

        plt.setp(ax0.get_xticklabels(), visible=False)
        # plt.setp(ax1.get_xticklabels(), visible=True)

        plt.subplots_adjust(left=.04, bottom=.14, right=.96, top=.95, wspace=.20, hspace=0)
        plt.show()
        # fig.savefig('example.png', facecolor=fig.get_facecolor())
