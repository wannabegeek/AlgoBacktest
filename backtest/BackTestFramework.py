import QuoteData


class BackTestFramework(object):
    algo = None
    dataProviders = []
    quotes = []
    context = None

    def __init__(self, dataProviderClass, algo, progressCallback = None):
        self.algo = algo
        self.progressCounter = 0
        self.progressCallback = progressCallback
        self.context = QuoteData.StrategyContext(self.algo.analysis_symbols())

        # if not isinstance(dataProvider, HistoricalQuoteRequest):
        #     raise TypeError("Data Provider must be of type 'HistoricalQuoteRequest'")

        if not self.algo.valid():
            raise TypeError("Algo provided isn't valid")

        for smbl in algo.analysis_symbols():
            self.dataProviders.append(dataProviderClass(smbl, self.algo.period()))

        self.positions = []
        self.currentPosition = None

        self.algo.initialiseContext(self.context)

        # request data and
        fn = lambda dataProvider, x : self.quotes.append({'quote' : x, 'provider' : dataProvider})
        for dataProvider in self.dataProviders:
            dataProvider.request(fn)

        # now that we have all the quotes, lets sort them by time
        # and publish them to the algo
        for quote in sorted(self.quotes, key=lambda x: x['quote'].timestamp, reverse=False):
            self.handleData(quote['provider'], quote['quote'])

    def handleData(self, dataProvjder, quote):
        if quote is None or not isinstance(quote, QuoteData.Quote):
            raise AssertionError("Invalid quote")

        self.context.addQuote(quote)
        for position in self.context.openPositions:
            position.update(quote)
        # logging.debug("Received Quote %s", quote)
        self.algo.evaluateTickUpdate(self.context, quote)
        if self.progressCallback is not None:
            self.progressCounter += 1
            self.progressCallback(float(self.progressCounter)/float(len(self.quotes)))

    def context(self):
        return self.context
