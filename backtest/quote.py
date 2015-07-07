from bisect import bisect_left
from datetime import datetime
import logging
from backtest.position import Position, PositionDirection, PositionStopType, PositionExitReason
from backtest.symbol import Symbol

class SymbolContext(object):
    """
    Context for a symbol contained within a StategyContext
    This holds symbol data and all the historical prices used for analysis

    You can also store and access custom variables using the [] accessor/mutator
    """

    def __init__(self, symbol):
        self.symbol = symbol
        self.lastUpdate = None
        self.quoteCache = {}
        self.cache = {}

        self.timestamp = None
        self.price = 0.0
        self.open = 0.0
        self.close = 0.0
        self.high = 0.0
        self.low = 0.0

    def addQuote(self, quote):
        """
        Add a quote to this symbol context
        :param quote: quote to add
        :return: None
        """
        # t = time.mktime(quote.timestamp.timetuple())
        t = quote.timestamp
        if t not in self.quoteCache:
            self.quoteCache[t] = quote
        self.cache = {}  # reset our cache
        self.lastUpdate = datetime.now()

        self.timestamp = quote.timestamp
        self.price = quote.close
        self.open = quote.open
        self.close = quote.close
        self.high = quote.high
        self.low = quote.low

    def quotes(self):
        """
        Return all quotes for this symbol context
        :return: A timestamp sorted list of all quotes for this symbol
        """
        if 'quotes' not in self.cache:
            self.cache['quotes'] = [self.quoteCache[k] for k in sorted(self.quoteCache.keys())]
        return self.cache['quotes']

    def quoteAtTime(self, timestamp):
        """
        Find the quote relevent at a specific time
        :param timestamp: timestamp to start search
        :return:A Quote object
        """
        if timestamp in self.quoteCache:
            return self.quoteCache[timestamp]
        keys = sorted(self.quoteCache.keys())
        val = bisect_left(keys, timestamp) - 1
        return self.quoteCache[keys[val]]

    def previousQuote(self, quote):
        """
        Find a quote previous to another
        :param quote: Quote object to start the search
        :return:A Quote object
        """
        keys = sorted(self.quoteCache.keys())
        val = bisect_left(keys, quote.timestamp) - 1
        if (val == -1):
            return None
        return self.quoteCache[keys[val]]

    def highs(self):
        """
        Get a list of all periods highs for this symbol context
        :return:List of all highs
        """
        if 'highs' not in self.cache:
            self.cache['highs'] = [x.high for x in self.quotes()]
        return self.cache['highs']

    def lows(self):
        """
        Get a list of all periods lows for this symbol context
        :return:List of all lows
        """
        if 'lows' not in self.cache:
            self.cache['lows'] = [x.low for x in self.quotes()]
        return self.cache['lows']

    def opens(self):
        """
        Get a list of all periods opens for this symbol context
        :return:List of all opens
        """
        if 'opens' not in self.cache:
            self.cache['opens'] = [x.open for x in self.quotes()]
        return self.cache['opens']

    def closes(self):
        """
        Get a list of all periods closes for this symbol context
        :return:List of all closes
        """
        if 'closes' not in self.cache:
            self.cache['closes'] = [x.close for x in self.quotes()]
        return self.cache['closes']

    def __getattr__(self, name):
        return self.__dict__[name]

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __str__(self):
        result = "Symbol: {0}\nLast Update: {1}\n\n".format(self.symbol, self.lastUpdate)
        for value in self.quotes():
            result += "\t{0}\n".format(value)
        return result

class StrategyContext(object):

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

    def openPosition(self, direction, quote, ratio = 1, stopLoss=-1, stopType = PositionStopType.FIXED, takeProfit=-1):
        """
        Open a position withing this strategy
        :param direction: Direction of the trade (LONG/SHORT)
        :param quote: The quote which has triggered this transaction
        :param ratio: The size of the trade (i.e. GBP per Point)
        :param stopLoss: The stop loss value, this is an absolute value i.e. the price at which to exit
        :param stopType: The type of stop loss. PositionStopType.TRAILING or PositionStopType.FIXED
        :param takeProfit: The price at which to take profit
        :return: The position object which is created
        """
        position = Position(quote.symbol, quote, direction, ratio, stopLoss, stopType, takeProfit)
        logging.info("Opening position {0}".format(position))
        self.openPositions.append(position)
        return position

    def closePosition(self, position, quote, reason = PositionExitReason.SIGNAL):
        """
        Close an open position
        :param position: The position to close
        :param quote: The quote causing the exit of the trade
        :param reason: The reason why the trade was closed (Default: PositionExitReason.SIGNAL)
        :return: None
        """
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