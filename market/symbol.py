from bisect import bisect_left
from collections import deque

from data.interfaces.symbol_data_provider import SymbolProviderData, SymbolProvider


class SymbolDataSource(object):
    YAHOO = 5
    GOOGLE = 6
    CMC_MARKETS = 7


class Symbol(object):

    _symbolDataProvider = None
    _symbol_cache = {}

    @staticmethod
    def setDataProvider(dataProvider):
        if not isinstance(dataProvider, SymbolProvider):
            raise TypeError("dataProvider must be of type SymbolDataProvider")
        Symbol._symbolDataProvider = dataProvider

    @staticmethod
    def get(sid):
        if sid in Symbol._symbol_cache:
            return Symbol._symbol_cache[sid]
        else:
            symbol = Symbol(sid)
            Symbol._symbol_cache[sid] = symbol
            return symbol

    def __init__(self, sid):
        if self._symbolDataProvider is None:
            raise RuntimeError("Symbol data provider hasn't been set")
        if sid in Symbol._symbol_cache:
            raise RuntimeError("Symbol %s already exists in the cache" % (sid,))

        self.sid = sid
        data = Symbol._symbolDataProvider.getDataForSymbol(sid)
        self.identifier = data[SymbolProviderData.identifier]
        self.name = data[SymbolProviderData.name]
        self.lot_size = data[SymbolProviderData.lot_size]

        self.lookup = {}

    def reference_symbol(self, dataSource):
        return self.lookup[dataSource]

    def __str__(self):
        return self.sid

    def __hash__(self):
        return self.identifier

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
        self.last_update = None

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

    def add_quote(self, quote):
        """
        Add a quote to this symbol context
        :param quote: quote to add
        :return: None
        """
        self.lastUpdate = quote.last_tick.timestamp
        self.timestamp = quote.start_time

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

    def previous_quote(self, quote):
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
