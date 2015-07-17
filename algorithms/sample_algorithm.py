import logging
import time

from numpy import asarray

from analysis import financial
from market.market_data import MarketDataPeriod
from market.order import Direction, Order, Entry, StopLoss
from strategy.strategy import Framework
from market.symbol import Symbol


class Algo(Framework):

    def __init__(self):
        super(Algo, self).__init__()
        self.maxPositions = 5
        pass

    def identifier(self):
        return "SampleStrategy"

    def warmupPeriod(self):
        """
        This is the number of periods required for the algorithm to warm up.
        i.e. how many periods should be process but not include in the overall performance
        This is useful for algorithms calculating results on previous period data. e.g. EMA requires data
        from the previous periods to calculate the current value.
        :return: The number of periods required for initialisation
        """
        return 26

    def portfolio_symbols(self):
        """
        This is a list of symbols which are used in the portfolio for this algorithm.
        :return: Array of Symbols used in this algorithm
        """
        return [Symbol('EURUSD:CUR'), ]

    # def analysis_symbols(self):
    #     """
    #     This is a list of symbols which are used for calculations in this algorithm.
    #     The default implementation of this method just calls self.portfolio_symbols()
    #     :return: Array of Symbols which the algorithm requires market data for.
    #     """
    #     return self.portfolio_symbols()

    def period(self):
        """
        This is the interval required for processing backdata.
        :return: Interval for the backdata
        """
        return MarketDataPeriod.MIN_5

    def initialiseContext(self, context):
        """
        This method can be used to initialise any context data objects or do any initialisation before
        the algorithm processing is started.
        The frame work calls this method before any market data updates
        """
        for symbol in self.analysis_symbols():
            context.symbolContexts[symbol].ema_10 = []
            context.symbolContexts[symbol].ema_25 = []
            context.symbolContexts[symbol].rsi_14 = []
            context.symbolContexts[symbol].position = False

    def evaluateTickUpdate(self, context, quote):
        """
        This method is called for every market data tick update on the requested symbols.
        """
        symbolContext = context.symbolContexts[quote.symbol]

        # logging.debug("I'm evaluating the data for %s" % (quote, ))

        if len(symbolContext.quotes) > 25:  # i.e. we have enough data
            quoteTimes = [time.mktime(o.startTime.timetuple()) for o in symbolContext.quotes]
            closePrices = asarray(symbolContext.closes)

            ema_10 = financial.ema(closePrices[-10:], 10)
            ema_25 = financial.ema(closePrices[-15:], 15)
            symbolContext.ema_10.append(ema_10)
            symbolContext.ema_25.append(ema_25)

            if ema_10 > ema_25:
                if context.symbolContexts[quote.symbol].position is False:
                    # create a LONG position
                    logging.debug("Opening position on quote: %s" % (quote,))
                    context.placeOrder(Order(quote.symbol, 1, Entry(Entry.Type.MARKET), Direction.LONG, stoploss=StopLoss(StopLoss.Type.FIXED, 20), takeProfit=25))
                    context.symbolContexts[quote.symbol].position = True
            else:
                if context.symbolContexts[quote.symbol].position is True:
                    context.symbolContexts[quote.symbol].position = False

            # gradientCount = 2
            # if len(symbolContext.ema_25) >= gradientCount:
            #     rsi_14 = financial.rsi(closePrices[-19:], 14)
            #     rsi_ema = financial.ema(rsi_14, 5)
            #     gradSMA_10 = mathmatical.gradient(symbolContext.ema_10[-gradientCount:], quoteTimes[-gradientCount:])
            #     gradSMA_25 = mathmatical.gradient(symbolContext.ema_10[-gradientCount:], quoteTimes[-gradientCount:])
            #
            #     positionsToClose = []
            #     # do we need to close any of our open positions?
            #     for position in context.openPositions:
            #         if position.shouldClosePosition(quote):
            #             positionsToClose.append(position)
            #         else:
            #             if position.direction == Direction.LONG:
            #                 if gradSMA_10 < 0 or gradSMA_25 < 0: # or rsi_ema[-1] >= 70):
            #                     positionsToClose.append(position)
            #                 # elif (quote.close - position.entryQuote.close) < -10.0:
            #                 #     context.closePosition(position, quote)
            #             elif position.direction == Direction.SHORT:
            #                 if gradSMA_10 > 0 or gradSMA_25 > 0: # or rsi_ema[-1] <= 50):
            #                     positionsToClose.append(position)
            #                 # elif (quote.close - position.entryQuote.close) > 10.0:
            #                 #     context.closePosition(position, quote)
            #
            #     # only take out a position if we don't already have one open
            #     if len(context.openPositions) == 0:
            #         # If have an upward trend and we were over-sold a few days ago
            #         logging.debug("Opening position")
            #         # if gradSMA_10 > 0 and gradSMA_25 > 0: # and rsi_ema[-1] < 50:
            #         #     context.openPosition(Direction.LONG, quote, 5, stopLoss=quote.low - 1000, stopType=PositionStopType.TRAILING)
            #         # elif gradSMA_10 < 0 and gradSMA_25 < 0: # and rsi_ema[-1] > 50:
            #         #     context.openPosition(Direction.SHORT, quote, 5, stopLoss=quote.high + 1000, stopType=PositionStopType.TRAILING)
            #
            #     for position in positionsToClose:
            #         context.closePosition(position, quote)
