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
        self.context = Context(working_capital, self.order_book, self.algo.analysis_symbols(), self.algo.warmupPeriod())

        self.algo.initialiseContext(self.context)

        self.order_book.addOrderStatusObserver(self.context, self.orderStatusObserver)
        self.order_book.addPositionStatusObserver(self.context, self.positionStatusObserver)

        for symbol in self.algo.analysis_symbols():
            self.data_provider.addPriceObserver(symbol, self.algo.period(), self.handleTickUpdate)

    def handleTickUpdate(self, symbol, quote):
        """
        This method gets called from the MarketData framework
        """
        # if quote is None or not isinstance(quote, Quote):
        #     raise TypeError("Invalid quote")

        self.context.add_quote(quote)
        self.algo.evaluateTickUpdate(self.context, quote)

    def orderStatusObserver(self, order, previous_state):
        if order.state is State.WORKING and previous_state is State.PENDING_NEW:
            logging.debug("Order accepted =================")
        elif order.state is State.FILLED and previous_state is State.WORKING:
            logging.debug("Order filled =================")

    def positionStatusObserver(self, position, previous_state):
        if previous_state is None:
            self.context.positions.append(position)
        elif not position.is_open():
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

