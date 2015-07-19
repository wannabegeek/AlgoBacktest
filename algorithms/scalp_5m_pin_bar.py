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
        return "5min Pinbar Scalp"

    def warmupPeriod(self):
        return 26

    def portfolio_symbols(self):
        return [Symbol('EURUSD:CUR'), ]

    def period(self):
        return MarketDataPeriod.MIN_5

    def initialiseContext(self, context):
        for symbol in self.analysis_symbols():
            context.symbolContexts[symbol].ema_25 = []
            context.symbolContexts[symbol].position = False

    def evaluateTickUpdate(self, context, quote):
        """
        This method is called for every market data tick update on the requested symbols.
        """
        symbolContext = context.symbolContexts[quote.symbol]

        # logging.debug("I'm evaluating the data for %s" % (quote, ))

        if len(symbolContext.quotes) > 25:  # i.e. we have enough data
            space = 5

            quoteTimes = [time.mktime(o.startTime.timetuple()) for o in symbolContext.quotes]
            closePrices = asarray(symbolContext.closes)

            ema_25 = financial.ema(closePrices[-25:], 25)
            symbolContext.ema_25.append(ema_25)

            bar_height = symbolContext.high - symbolContext.low
            # bar_is_largest = bar_height > (symbolContext.highs[-1] - symbolContext.lows[-1])
            bar_is_lowest = symbolContext.low < min(list(symbolContext.lows)[-space:-1])
            bar_is_highest = symbolContext.high > max(list(symbolContext.highs)[-space:-1])

            buy_signal = bar_is_lowest and ((min(symbolContext.open, symbolContext.close) - symbolContext.low) * 1.5) >= (symbolContext.high - symbolContext.low)
            sell_signal = bar_is_highest and ((symbolContext.high - max(symbolContext.open, symbolContext.close)) * 1.5) >= (symbolContext.high - symbolContext.low)

            if quote.close > ema_25 and sell_signal:
                # if context.symbolContexts[quote.symbol].position is False:
                    # create a LONG position
                logging.debug("Opening position on quote: %s" % (quote,))
                context.placeOrder(Order(quote.symbol, 1, Entry(Entry.Type.MARKET), Direction.SHORT, stoploss=StopLoss(StopLoss.Type.FIXED, 20), takeProfit=25))
                # context.symbolContexts[quote.symbol].position = True
            elif quote.close < ema_25 and buy_signal:
                logging.debug("Opening position on quote: %s" % (quote,))
                context.placeOrder(Order(quote.symbol, 1, Entry(Entry.Type.MARKET), Direction.LONG, stoploss=StopLoss(StopLoss.Type.FIXED, 20), takeProfit=25))

