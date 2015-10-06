import logging
import time
import datetime

from numpy import asarray

from analysis import financial
from market.market_data import MarketDataPeriod
from market.order import Direction, Order, Entry, StopLoss
from strategy.strategy import Framework
from market.symbol import Symbol


class Algo(Framework):

    def __init__(self, emaPeriod, stopLoss, takeProfit):
        super(Algo, self).__init__()
        self.maxPositions = 2
        self.emaPeriod = emaPeriod
        self.stopLoss = StopLoss(StopLoss.Type.FIXED, stopLoss)
        self.takeProfit = takeProfit
        pass

    def identifier(self):
        return "5min Pinbar Scalp (ema: %s, sl:%s, tp:%s)" % (self.emaPeriod, self.stopLoss.points, self.takeProfit)

    def quote_cache_size(self):
        return self.emaPeriod + 1

    def analysis_symbols(self):
        return [Symbol.get('EURUSD:CUR'), ]

    def period(self):
        return MarketDataPeriod.MIN_5

    def initialise_context(self, context):
        for symbol in self.analysis_symbols():
            context.symbol_contexts[symbol].ema = []
            context.symbol_contexts[symbol].positiocn = False

    def evaluate_quote_update(self, context, quote):
        """
        This method is called for every market data tick update on the requested symbols.
        """
        symbolContext = context.symbol_contexts[quote.symbol]

        # logging.debug("I'm evaluating the data for %s" % (quote, ))

        if len(symbolContext.quotes) > self.emaPeriod:  # i.e. we have enough data
            space = 5

            if quote.start_time.time() > datetime.time(21, 0) or quote.start_time.time() < datetime.time(7, 0):
                # not normal EURUSD active period
                return
            if quote.start_time.weekday() >= 5:
                # it's a weekend
                return
            if quote.start_time.weekday() == 4 and quote.start_time.time() > datetime.time(12, 0):
                # no positions after 12 on Friday
                return

            closePrices = asarray(symbolContext.closes)
            ema = financial.ema(closePrices[-self.emaPeriod:], self.emaPeriod)

            bar_height = symbolContext.high - symbolContext.low
            # bar_is_largest = bar_height > (symbolContext.highs[-1] - symbolContext.lows[-1])
            bar_is_lowest = symbolContext.low < min(list(symbolContext.lows)[-space:-1])
            bar_is_highest = symbolContext.high > max(list(symbolContext.highs)[-space:-1])

            buy_signal = bar_is_lowest and ((min(symbolContext.open, symbolContext.close) - symbolContext.low) * 1.5) >= (symbolContext.high - symbolContext.low)
            sell_signal = bar_is_highest and ((symbolContext.high - max(symbolContext.open, symbolContext.close)) * 1.5) >= (symbolContext.high - symbolContext.low)
            open_positions = list(context.open_positions())

            if quote.close > ema and sell_signal:
                # if context.quote_contexts[quote.symbol].position is False:
                    # create a LONG position
                if len(open_positions) != 0:
                    position = open_positions[0]
                    if position.order.direction is Direction.SHORT:
                        context.close_position(position)
                else:
                    logging.debug("Opening position on quote: %s" % (quote,))
                    context.place_order(Order(quote.symbol, 50, Entry(Entry.Type.MARKET), Direction.SHORT, stoploss=self.stopLoss, take_profit=self.takeProfit))
                # context.quote_contexts[quote.symbol].position = True
            elif quote.close < ema and buy_signal:
                if len(open_positions) != 0:
                    position = open_positions[0]
                    if position.order.direction is Direction.LONG:
                        context.close_position(position)
                else:
                    logging.debug("Opening position on quote: %s" % (quote,))
                    context.place_order(Order(quote.symbol, 50, Entry(Entry.Type.MARKET), Direction.SHORT, stoploss=self.stopLoss, take_profit=self.takeProfit))

