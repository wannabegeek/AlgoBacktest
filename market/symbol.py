from bisect import bisect_left
from collections import deque
import datetime


class SymbolDataSource(object):
    YAHOO = 5
    GOOGLE = 6
    CMC_MARKETS = 7

class Symbol(object):

    _symbolDataProvider = None
    _symbolState = {}

    @staticmethod
    def setDataProvider(dataProvider):
        Symbol._symbolDataProvider = dataProvider

    def __init__(self, identifier):
        if self._symbolDataProvider is None:
            raise RuntimeError("Symbol data provider hasn't been set")

        if identifier in self._symbolState:
            self.__dict__ = self._symbolState[identifier]
        else:
            self.identifier = identifier
            self.name = None
            self.lookup = {}
            self.lot_size = 10000
            self._symbolState[identifier] = self.__dict__

        # cursor = self._dbConnection.cursor(buffered=True)
        # cursor.callproc('SymbolInfo', [self.identifier, ])
        # for result in cursor.stored_results():
        #     results = result.fetchall()
        #     if len(results) == 0:
        #         raise LookupError("Symbol: '{0}' Not Found".format(self.identifier))
        #     for result in results:
        #         self.spread = result[4]
        # cursor.close()
        #
        # cursor = self._dbConnection.cursor(buffered=True)
        # cursor.callproc('GetSymbol', [self.identifier, ])
        # for result in cursor.stored_results():
        #     results = result.fetchall()
        #     if len(results) == 0:
        #         raise LookupError("Symbol: '{0}' Not Found".format(self.identifier))
        #     for result in results:
        #         self.name = result[1]
        #         self.lookup[result[2]] = result[3]
        # cursor.close()

    def referenceSymbol(self, dataSource):
        return self.lookup[dataSource]

    def __str__(self):
        return "Symbol: %s" % (self.identifier,)

    def __hash__(self):
        return hash(str(self.identifier))

    def __eq__(self, other):
        return self.identifier == other.identifier

    __repr__ = __str__

class SymbolContext(object):
    """
    Context for a symbol contained within a StategyContext
    This holds symbol data and all the historical prices used for analysis

    You can also store and access custom variables using the [] accessor/mutator
    """
    def __init__(self, symbol, history_size):
        self.symbol = symbol
        self.lastUpdate = None

        self.timestamp = None
        self.price = 0.0
        self.open = 0.0
        self.close = 0.0
        self.high = 0.0
        self.low = 0.0

        self.quotes = deque(maxlen=history_size) 
        self.opens = deque(maxlen=history_size)
        self.highs = deque(maxlen=history_size)
        self.lows = deque(maxlen=history_size)
        self.closes = deque(maxlen=history_size)

    def addQuote(self, quote):
        """
        Add a quote to this symbol context
        :param quote: quote to add
        :return: None
        """
        self.lastUpdate = quote.lastTick.timestamp
        self.timestamp = quote.startTime

        self.price = quote.close
        self.open = quote.open
        self.close = quote.close
        self.high = quote.high
        self.low = quote.low

        self.opens.append(quote.open)
        self.highs.append(quote.high)
        self.lows.append(quote.low)
        self.closes.append(quote.close)

        self.quotes.append(quote)

    # def quoteAtTime(self, timestamp):
    #     """
    #     Find the quote relevant at a specific time
    #     :param timestamp: timestamp to start search
    #     :return: A Quote object
    #     """
    #     if timestamp in self.quoteCache:
    #         return self.quoteCache[timestamp]
    #     keys = sorted(self.quoteCache.keys())
    #     val = bisect_left(keys, timestamp) - 1
    #     return self.quoteCache[keys[val]]

    def previousQuote(self, quote):
        """
        Find a quote previous to another
        :param quote: Quote object to start the search
        :return: A Quote object
        """
        index = bisect_left(self.quotes, quote) - 1
        if (index == -1):
            return None
        return self.quotes[index]


    def __str__(self):
        return "Symbol: %s Last Quote Time: %s Quotes: %d" % (self.symbol, self.timestamp, len(self.quotes))

    __repr__ = __str__
