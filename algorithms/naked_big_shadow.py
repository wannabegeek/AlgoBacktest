from market.market_data import MarketDataPeriod
from market.order import Direction, Order, Entry, StopLoss
from strategy.strategy import Framework
from market.symbol import Symbol

import math

#
# TODO: make sure this only prints on a zone
#
class NakedBigShadow(Framework):

    def __init__(self, space_to_left, largest_body_count, take_profit, period):
        super(NakedBigShadow, self).__init__()
        self.take_profit = take_profit
        self.time_period = period

        self.pct_risk = 0.02  # risk ratio in 100ths of a %

        self.space_to_left = space_to_left
        self.largest_body_count = largest_body_count
        pass

    def identifier(self):
        return "Naked Big Shadow"

    def secondary_identifier(self):
        return "space_to_left: %s, lbc:%s, period:%s, tp:%s" % (self.space_to_left, self.largest_body_count, self.time_period, self.take_profit)

    def quote_cache_size(self):
        return max(self.space_to_left, self.largest_body_count) + 1

    def analysis_symbols(self):
        return [(self.time_period, Symbol.get('EURUSD:CUR')), (MarketDataPeriod.MIN_5, Symbol.get('EURUSD:CUR'))]

    def period(self):
        return self.time_period

    def initialise_context(self, context):
        pass

    def is_opposite(self, current, previous):
        return (current.close >= current.open and previous.close <= previous.open) or (current.close <= current.open and previous.close >= previous.open)

    def is_body_engulfing(self, current, previous):
        return max(current.open, current.close) >= max(previous.open, previous.close) and min(current.open, current.close) <= min(previous.open, previous.close)

    def is_strong_candle(self, quote, direction):
        # i.e. the close needs to be towards the extreems of the range
        # the closing price must be within 25% of the high/low
        range = quote.high - quote.low
        if range > 0.0:
            if direction is Direction.LONG:
                close = quote.high - quote.close
                ratio = close / range
                return ratio <= 0.25
            else:
                close = quote.close - quote.low
                ratio = close / range
                return ratio <= 0.25
        return False

    def is_largest(self, quote, history):
        current_range = abs(quote.open - quote.close)
        for q in history:
            if current_range < abs(q.open - q.close):
                return False
        return True

    def has_space_to_left_of_high(self, quote, previous_quote, history):
        high = max(quote.high, previous_quote.high)
        for q in history:
            if high < q.high:
                return False
        return True

    def has_space_to_left_of_low(self, quote, previous_quote, history):
        low = min(quote.low, previous_quote.low)
        for q in history:
            if low > q.low:
                return False
        return True

    def should_make_zero_risk(self, position, quote):
        # if we are 50% of the way to our profit target, move the stop loss to 0
        points_delta = position.points_delta(quote.close)
        return points_delta >= position.take_profit / 2.0

    def should_guarantee_profit(self, position, quote):
        # if we are 75% of the way to our profit target, move the stop loss
        points_delta = position.points_delta(quote.close)
        return points_delta >= position.take_profit / 1.5

    def calculate_position_size(self, context, stop_loss):
        # we only want to risk a small amount of our capital
        risk = context.working_capital * self.pct_risk
        return int(math.floor(risk / stop_loss))
        
    def evaluate_quote_update(self, context, quote):
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

            previous_quote = symbol_context.quotes[-1]

            # have we changed direction?
            if self.is_opposite(quote, previous_quote):
                # check if this candle engulfs the previous
                if self.is_body_engulfing(quote, previous_quote):
                    historic_periods = list(symbol_context.quotes)[:-1]
                    if self.is_largest(quote, historic_periods[-self.largest_body_count:]):
                        # are we thinking about long or short?
                        if quote.close < quote.open:  # go short
                            if self.is_strong_candle(quote, Direction.SHORT):
                                if self.has_space_to_left_of_high(quote, previous_quote, historic_periods[-self.space_to_left:-1]):
                                    stop_points = (abs(quote.close - quote.high) * (quote.symbol.lot_size + 1)) + 5
                                    stop_loss = StopLoss(StopLoss.Type.FIXED, stop_points)
                                    qty = self.calculate_position_size(context, stop_points)
                                    if qty > 0:
                                        context.place_order(Order(quote.symbol, qty, Entry(Entry.Type.LIMIT, quote.low - 5), Direction.SHORT, stoploss=stop_loss, take_profit=self.take_profit, expire_time=self.time_period))
                        else:  # go long
                            if self.is_strong_candle(quote, Direction.LONG):
                                if self.has_space_to_left_of_low(quote, previous_quote, historic_periods[-self.space_to_left:-1]):
                                    stop_points = (abs(quote.close - quote.low) * (quote.symbol.lot_size + 1)) + 5
                                    stop_loss = StopLoss(StopLoss.Type.FIXED, stop_points)
                                    qty = self.calculate_position_size(context, stop_points)
                                    if qty > 0:
                                        context.place_order(Order(quote.symbol, qty, Entry(Entry.Type.LIMIT, quote.high + 5), Direction.LONG, stoploss=stop_loss, take_profit=self.take_profit, expire_time=self.time_period))

                open_positions = list(context.open_positions())
                for position in open_positions:
                    # TODO: check if our stop_price is already >= entry_price
                    if self.should_guarantee_profit(position, quote):
                        position.update(stop_loss=StopLoss(StopLoss.Type.FIXED, position.take_profit / -2.0))
                    elif self.should_make_zero_risk(position, quote):
                        position.update(stop_loss=StopLoss(StopLoss.Type.FIXED, 0.0))

