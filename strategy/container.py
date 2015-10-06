import logging

from market.market_data import MarketData
from market.order import State
from market.orderbook import OrderBook
from market.position import Position
from market.price import Quote
from strategy.strategy import Framework, Context
from market.symbol import Symbol


class Container(object):
    def __init__(self, algo, working_capital, order_book, data_provider):
        if not isinstance(algo, Framework):
            raise TypeError("algorithm must be a subclass of strategy.strategy.Framework")
        if not isinstance(order_book, OrderBook):
            raise TypeError("order_book must be a subclass of OrderBook")
        if not isinstance(data_provider, MarketData):
            raise TypeError("data_provider must be a subclass of MarketData")

        self.algo = algo
        self.starting_capital = working_capital
        self.order_book = order_book
        self.data_provider = data_provider
        self.context = Context(working_capital, self.order_book, self.algo.analysis_symbols(), self.algo.quote_cache_size())

        self.algo.initialise_context(self.context)

        self.order_book.addOrderStatusObserver(self.context, self.order_status_update)
        self.order_book.addPositionStatusObserver(self.context, self.position_status_observer)

        for symbol in self.algo.analysis_symbols():
            self.data_provider.addPriceObserver(symbol, self.algo.period(), self.handle_tick_update)

    def handle_tick_update(self, symbol, quote):
        """
        This method gets called from the MarketData framework
        """
        # if quote is None or not isinstance(quote, Quote):
        #     raise TypeError("Invalid quote")

        self.algo.evaluate_quote_update(self.context, quote)
        self.context.add_quote(quote)

    def order_status_update(self, order, previous_state):
        if order.status is State.WORKING and previous_state is State.PENDING_NEW:
            logging.debug("Order accepted =================")
        elif order.status is State.FILLED and previous_state is State.WORKING:
            logging.debug("Order filled =================")

    def position_status_observer(self, position, previous_state):
        if previous_state is None and position not in self.context.positions:
            self.context.positions.append(position)
        elif not position.is_open() and position in self.context.positions:
            self.context.working_capital += position.points_delta() * position.order.quantity

    def __str__(self):
        total_positions = len(list(filter(lambda x: not x.is_open(), self.context.positions)))

        if total_positions == 0:
            return "========================\nAlgo %s\nNo Positions taken" % (self.algo.identifier(),)
        else:
            closed = list(map(lambda x: "%s  --> %.2fpts (%s)" % (x, x.points_delta(), x.position_time()), filter(lambda x: not x.is_open(), self.context.positions)))
            open = list(map(lambda x: "%s" % (x), filter(lambda x: x.is_open(), self.context.positions)))
            winning = list(filter(lambda x: x.points_delta() > 0.0, filter(lambda x: not x.is_open(), self.context.positions)))

            return "========================\nAlgo %s\nCompleted:\n%s\nOpen:\n%s\nWinning Ratio: %.2f%%\nTotal Pts: %.2f" % (self.algo.identifier(), "\n".join(closed),
                                                                       "\n".join(open),
                                                                       (len(winning)/total_positions * 100),
                                                                       sum([x.points_delta() for x in filter(lambda x: not x.is_open(), self.context.positions)]))

