import logging
import time
import datetime

from numpy import asarray

from analysis import financial
from market.market_data import MarketDataPeriod
from market.order import Direction, Order, Entry, StopLoss
from strategy.strategy import Framework
from market.symbol import Symbol


class NakedReversalAlgo(Framework):

    def __init__(self, space_to_left, stop_loss, take_profit):
        super(NakedReversalAlgo, self).__init__()
        self.stop_loss = StopLoss(StopLoss.Type.FIXED, stop_loss)
        self.take_profit = take_profit

        self.space_to_left = space_to_left
        pass

    def identifier(self):
        return "Naked 1H Reversal (space_to_left: %s, sl:%s, tp:%s)" % (self.space_to_left, self.stop_loss.points, self.take_profit)

    def warmupPeriod(self):
        return self.space_to_left + 1

    def portfolio_symbols(self):
        return [Symbol.get('EURUSD:CUR'), ]

    def period(self):
        return MarketDataPeriod.HOUR_1

    def initialiseContext(self, context):
        pass

    def evaluateTickUpdate(self, context, quote):
        """
        This method is called for every market data tick update on the requested symbols.
        """
        symbol_context = context.symbolContexts[quote.symbol]

        if len(symbol_context.quotes) > self.warmupPeriod() - 1:  # i.e. we have enough data

            if quote.startTime.time() > datetime.time(21, 0) or quote.startTime.time() < datetime.time(7, 0):
                # not normal EURUSD active period
                return
            if quote.startTime.weekday() >= 5:
                # it's a weekend
                return
            if quote.startTime.weekday() == 4 and quote.startTime.time() > datetime.time(16, 0):
                # no positions after 16:00 on Friday
                return

            if symbol_context.close <= symbol_context.closes[-2] and symbol_context.open >= symbol_context.opens[-2]:
                # we have an engulfing body
                if symbol_context.open < symbol_context.close:
                    # buying oppertunity
                    # since this is 2 candle set up, find the lowes of the current an previous
                    low = min(symbol_context.low, symbol_context.lows[-2])
                    if low < min(list(symbol_context.lows)[:-3]):
                        context.placeOrder(Order(quote.symbol, 10, Entry(Entry.Type.MARKET), Direction.LONG, stoploss=self.stop_loss, takeProfit=self.take_profit))
                else:
                    # selling oppertunity
                    high = min(symbol_context.high, symbol_context.high[-2])
                    if high > max(list(symbol_context.highs)[:-3]):
                        context.placeOrder(Order(quote.symbol, 10, Entry(Entry.Type.MARKET), Direction.SHORT, stoploss=self.stop_loss, takeProfit=self.take_profit))

            # open_positions = list(context.getOpenPositions())

            # if quote.close > ema and sell_signal:
            #     # if context.symbolContexts[quote.symbol].position is False:
            #         # create a LONG position
            #     if len(open_positions) != 0:
            #         position = open_positions[0]
            #         if position.order.direction is Direction.LONG:
            #             context.closePosition(position)
            #     else:
            #         logging.debug("Opening position on quote: %s" % (quote,))
            #         context.placeOrder(Order(quote.symbol, 50, Entry(Entry.Type.MARKET), Direction.SHORT, stoploss=self.stopLoss, takeProfit=self.takeProfit))
            #     # context.symbolContexts[quote.symbol].position = True
            # elif quote.close < ema and buy_signal:
            #     if len(open_positions) != 0:
            #         position = open_positions[0]
            #         if position.order.direction is Direction.SHORT:
            #             context.closePosition(position)
            #     else:
            #         logging.debug("Opening position on quote: %s" % (quote,))
            #         context.placeOrder(Order(quote.symbol, 50, Entry(Entry.Type.MARKET), Direction.LONG, stoploss=self.stopLoss, takeProfit=self.takeProfit))

