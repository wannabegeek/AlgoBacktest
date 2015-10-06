from abc import ABCMeta, abstractmethod
import logging

from market.order import State
from market.orderbook import OrderBook
from market.position import Position
from market.symbol import QuoteContext


class Framework(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.currentContext = None
        pass

    def quote_cache_size(self):
        """
        This is the number of quotes required to be cached for the algorithm.
        This is useful for algorithms calculating results on previous period data. e.g. EMA requires data
        from the previous periods to calculate the current value.
        :return: The number of periods required for caching
        """
        return 1

    def initialise_context(self, context):
        """
        This method can be used to initialise any context data objects or do any initialisation before
        the algorithm processing is started.
        The frame work calls this method before any market data updates
        """
        pass

    @abstractmethod
    def identifier(self):
        pass

    @abstractmethod
    def analysis_symbols(self):
        """
        This is a list of symbols & periods which are used in this algorithm.
        :return: Array of period & Symbol tuples used in this algorithm
        """
        pass

    @abstractmethod
    def evaluate_quote_update(self, context, quote):
        """
        This method is called for every market data tick update on the requested symbols.
        """
        pass

    def __hash__(self):
        return hash(self.identifier())


class Context(object):
    def __init__(self, working_capital, order_book, market_data, history_size):
        """
        Constructor
        This is for internal use.
        :param order_manager: OrderManager which coordinates getting orders to market
        :param symbols: A List of symbols used in this Strategy
        :return: A StrategyContext object
        """
        if not isinstance(order_book, OrderBook):
            raise TypeError('order_book must be an OrderBook object type')

        self.working_capital = working_capital
        self.order_book = order_book
        self.quote_contexts = {}

        for (symbol, period, callback) in market_data:
            context = QuoteContext(symbol, period, history_size)
            self.quote_contexts[(symbol, period)] = context

        self.orders = []
        self.positions = []
        self.custom_data = dict()
        self.start_time = None

    def add_quote(self, quote):
        """
        Add a quote to the strategy context.
        This is for internal use.
        :param quote: The quote to add
        """
        context = self.get_quote_context(quote)
        context.add_quote(quote)
        if self.start_time is None:
            self.start_time = quote.start_time

    def get_quote_context(self, quote):
        return self.quote_contexts[(quote.symbol, quote.period)]

    def get_quote_context_by_symbol(self, symbol, period):
        return self.quote_contexts[(symbol, period)]

    def place_order(self, order):
        """
        Place an order on the market.
        :param order: The order to add
        :return: The order placed (same as passed in)
        """

        self.order_book.place_order(self, order)

        # if this is a market order, it will be filled on the next tick
        self.orders.append(order)
        return order

    def cancel_order(self, order):
        """
        Cancel a resting  order on the market.
        The status change of the order will be notified by the statusCallback function the placeOrder method
        :param order: The order to modify
        """
        self.order_book.cancel_order(self, order)

    def close_position(self, position, reason = Position.PositionStatus.CLOSED):
        """
        Close an open position
        :param position: The position to close
        :param reason: The reason why the trade was closed (Default: Position.ExitReason.CLOSED)
        :return: None
        """
        if not isinstance(position, Position):
            raise TypeError('position must be an Position object type')

        self.order_book.close_position(position)
        logging.debug("Closing position {0}".format(position))

    def record(self, key, value, quote):
        """
        Record a custom value.
        This is useful for plotting custom data in an output graph for analysis
        :param key: The name for the data you are adding
        :param value: The custom value to store
        :param quote: The quote causing the data update (used for timestamp)
        :return: None
        """
        try:
            self.custom_data[key][quote.timestamp] = value
        except KeyError as e:
            self.custom_data[key] = dict()
            self.custom_data[key][quote.timestamp] = value

    def open_positions(self):
        """
        Get a list of all open positions
        :return: List of positions
        """
        return filter(lambda x: x.status == Position.PositionStatus.OPEN, self.positions)

    def open_orders(self):
        """
        Get a list of all open positions
        :return: List of positions
        """
        return filter(lambda x: x.state == State.PENDING_NEW, self.orders)

    def __getattr__(self, name):
        return self.__dict__[name]

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __getstate__(self):
        state = {}
        state['symbol'] = self.symbol
        state['last_update'] = self.lastUpdate
        state['data'] = self.quoteCache
        return state

    def __setstate__(self, state):
        self.symbol = state['symbol']
        self.lastUpdate = state['last_update']
        self.quoteCache = state['data']

    def __str__(self):
        result = "Symbol: {0}\nLast Update: {1}\n\n".format(self.symbol.name, self.lastUpdate)
        for k, value in sorted(self.quoteCache.items()):
            result += "\t{0}\n".format(value)
        return result
