
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
            self.spread = 1.0
            self.leverage = 5
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
        return "Symbol: {0} Last Update: {1}" % (self.symbol, self.lastUpdate)

    __repr__ = __str__
