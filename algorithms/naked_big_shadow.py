from market.market_data import MarketDataPeriod
from market.order import Direction, Order, Entry, StopLoss
from strategy.strategy import Framework
from market.symbol import Symbol

#
# TODO: make sure this only prints on a zone
#
class NakedBigShadow(Framework):

    def __init__(self, space_to_left, stop_loss, take_profit):
        super(NakedBigShadow, self).__init__()
        self.stop_loss = StopLoss(StopLoss.Type.FIXED, stop_loss)
        self.take_profit = take_profit

        self.space_to_left = space_to_left
        pass

    def identifier(self):
        return "Naked 1H Reversal (space_to_left: %s, sl:%s, tp:%s)" % (self.space_to_left, self.stop_loss.points, self.take_profit)

    def quote_cache_size(self):
        return self.space_to_left + 1

    def analysis_symbols(self):
        return [Symbol.get('EURUSD:CUR'), ]

    def period(self):
        return MarketDataPeriod.HOUR_4

    def initialise_context(self, context):
        pass

    def is_opposite(self, current, previous):
        return (current.close >= current.open and previous.close <= previous.open) or (current.close <= current.open and previous.close >= previous.open)

    def is_body_engulfing(self, current, previous):
        return max(current.open, current.close) >= max(previous.open, previous.close) and min(current.open, current.close) <= min(previous.open, previous.close)

    def is_strong_candle(self, quote, direction):
        # i.e. the close needs to be towards the extreems of the range
        # the closing price must be within 25% of the high/low
        if direction is Direction.LONG:
            close = quote.high - quote.close
            range = quote.high - quote.low
            ratio = close / range
            return ratio <= 0.25
        else:
            close = quote.close - quote.low
            range = quote.high - quote.low
            ratio = close / range
            return ratio <= 0.25

    def should_make_zero_risk(self, position, quote):
        points_delta = position.points_delta(quote.close)
        return points_delta >= position.take_profit / 2.0


    def evaluate_tick_update(self, context, quote):
        """
        This method is called for every market data tick update on the requested symbols.
        """
        symbol_context = context.symbol_contexts[quote.symbol]

        if len(symbol_context.quotes) > self.space_to_left:  # i.e. we have enough data

            # if quote.start_time.time() > datetime.time(21, 0) or quote.start_time.time() < datetime.time(7, 0):
            #     # not normal EURUSD active period
            #     return
            # if quote.start_time.weekday() >= 5:
            #     # it's a weekend
            #     return
            # if quote.start_time.weekday() == 4 and quote.start_time.time() > datetime.time(16, 0):
            #     # no positions after 16:00 on Friday
            #     return

            previous_quote = symbol_context.quotes[-2]

            # have we changed direction?
            if self.is_opposite(quote, previous_quote):
                # check if this candle engulfs the previous
                if self.is_body_engulfing(quote, previous_quote):
                    # are we the largest candle for X periods
                    # are we thinking about long or short?
                    if quote.close < quote.open:
                        # go short
                        # how far from the low is our close?
                        if self.is_strong_candle(quote, Direction.SHORT):
                            # do we have space to left
                            high = max(quote.high, previous_quote.high)
                            if high < max(list(symbol_context.highs)[:-3]):
                                stop_loss = StopLoss(StopLoss.Type.FIXED, (abs(quote.close - quote.high) * (quote.symbol.lot_size + 1)) + 5)
                                context.place_order(Order(quote.symbol, 10, Entry(Entry.Type.LIMIT, quote.low), Direction.SHORT, stoploss=stop_loss, take_profit=self.take_profit, expire_time=MarketDataPeriod.HOUR_4))
                    else:
                        # go long
                        # how far from the high is our open?
                        if self.is_strong_candle(quote, Direction.LONG):
                            # do we have space to left
                            low = min(quote.low, previous_quote.low)
                            if low < min(list(symbol_context.lows)[:-3]):
                                stop_loss = StopLoss(StopLoss.Type.FIXED, (abs(quote.close - quote.low) * (quote.symbol.lot_size + 1)) + 5)
                                context.place_order(Order(quote.symbol, 10, Entry(Entry.Type.LIMIT, quote.high), Direction.LONG, stoploss=stop_loss, take_profit=self.take_profit, expire_time=MarketDataPeriod.HOUR_4))

                open_positions = list(context.open_positions())
                for position in open_positions:
                    if self.should_make_zero_risk(position, quote):
                        position.update(stoploss=StopLoss(StopLoss.Type.FIXED, 0.0))
