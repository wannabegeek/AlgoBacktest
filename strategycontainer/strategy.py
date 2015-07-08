from abc import ABCMeta, abstractmethod
import logging
from strategycontainer.order import Order, State
from strategycontainer.position import Position
from strategycontainer.symbol import SymbolContext, Symbol


class Framework(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.currentContext = None
        pass

    def warmupPeriod(self):
        return 0

    def analysis_symbols(self):
        return self.portfolio_symbols()

    @abstractmethod
    def portfolio_symbols(self):
        pass

    @abstractmethod
    def period(self):
        pass

    def initialiseContext(self, context):
        pass;

    @abstractmethod
    def evaluateTickUpdate(self, context, quote):
        pass


class Context(object):
    def __init__(self, symbols):
        """
        Constructor
        This is for internal use.
        :param symbols: A List of symbols used in this Strategy
        :return: A StrategyContext object
        """
        self.symbolContexts = {}
        for symbol in symbols:
            logging.debug("Creating symbol context for {0}".format(symbol))
            context = SymbolContext(symbol)
            self.symbolContexts[symbol] = context

        self.orders = []
        self.positions = []
        self.custom_data = dict()

    def addQuote(self, quote):
        """
        Add a quote to the strategy context.
        This is for internal use.
        :param quote: The quote to add
        """
        context = self.symbolContexts[quote.symbol]
        context.addQuote(quote)

    def symbolData(self, symbol):
        return self.symbolContexts[symbol]

    def placeOrder(self, order, statusCallback = None):
        """
        Place an order on the market.
        :param order: The order to add
        :param statusCallback: Callback function reporting any status changes
        :return: The order placed (same as passed in)
        """
        if not isinstance(order, Order):
            raise TypeError('order must be an Order object type')
        logging.info("Releasing order {0}".format(order))
        # if this is a market order, it will be filled on the next tick
        self.orders.append(order)
        return order

    def cancelOrder(self, order):
        """
        Cancel a resting  order on the market.
        The status change of the order will be notified by the statusCallback function the placeOrder method
        :param order: The order to modify
        """
        if not isinstance(order, Order):
            raise TypeError('order must be an Order object type')

    def openPosition(self, position):
        if not isinstance(position, Position):
            raise TypeError('position must be an Position object type')

        self.positions.append(position)

    def closePosition(self, position, reason = Position.ExitReason.CLOSED):
        """
        Close an open position
        :param position: The position to close
        :param reason: The reason why the trade was closed (Default: Position.ExitReason.CLOSED)
        :return: None
        """
        if not isinstance(position, Position):
            raise TypeError('position must be an Position object type')

        position.close(quote, reason)
        logging.info("Closing position {0}".format(position))

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


    def getOpenPositions(self):
        """
        Get a list of all open positions
        :return: List of positions
        """
        return filter(lambda x: x.exitReason == Position.ExitReason.NOT_CLOSED, self.positions)

    def getOpenOrders(self):
        """
        Get a list of all open positions
        :return: List of positions
        """
        return filter(lambda x: x.state == State.WORKING, self.orders)

    def __getattr__(self, name):
        return self.__dict__[name]

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __getstate__(self):
        state = {}
        state['symbol'] = self.symbol
        state['lastUpdate'] = self.lastUpdate
        state['data'] = self.quoteCache
        return state

    def __setstate__(self, state):
        self.symbol = state['symbol']
        self.lastUpdate = state['lastUpdate']
        self.quoteCache = state['data']

    def __str__(self):
        result = "Symbol: {0}\nLast Update: {1}\n\n".format(self.symbol.name, self.lastUpdate)
        for k, value in sorted(self.quoteCache.items()):
            result += "\t{0}\n".format(value)
        return result