from abc import ABCMeta, abstractmethod
import logging
from strategycontainer.order import Order
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

        self.openOrders = []
        self.openPositions = []
        self.closedPositions = []
        self.custom_data = dict()

    def addQuote(self, quote):
        """
        Add a quote to the strategy context.
        This is for internal use.
        :param quote: The quote to add
        """
        if quote.symbol is None or not isinstance(quote.symbol, Symbol):
            raise AssertionError("Quote has invalid symbol")

        context = self.symbolContexts[quote.symbol]
        context.addQuote(quote)

    def symbolData(self, symbol):
        return self.symbolContexts[symbol]

    def releaseOrder(self, order, filledCallback = None):
        if not isinstance(order, Order):
            raise TypeError('order must be an Order object type')
        logging.info("Releasing order {0}".format(order))
        # if this is a market order, it will be filled on the next tick
        self.openOrders.append(order)

    def closePosition(self, position, quote, reason = Position.ExitReason.CLOSED):
        """
        Close an open position
        :param position: The position to close
        :param quote: The quote causing the exit of the trade
        :param reason: The reason why the trade was closed (Default: Position.ExitReason.CLOSED)
        :return: None
        """
        if not isinstance(position, Position):
            raise TypeError('position must be an Position object type')

        position.close(quote, reason)
        logging.info("Closing position {0}".format(position))
        self.openPositions.remove(position)
        self.closedPositions.append(position)

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
        return self.openPositions

    def getOpenOrders(self):
        """
        Get a list of all open positions
        :return: List of positions
        """
        return self.openOrders

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