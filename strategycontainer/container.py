import logging
from data.data_provider import Provider
from strategycontainer.price import PriceConflator, Quote
from strategycontainer.strategy import Framework, Context


class Container(object):
    def __init__(self, algo, priceDataProvider, progressCallback = None):
        if not isinstance(algo, Framework):
            raise TypeError("algorithm must be a subclass of strategycontainer.strategy.Framework")
        if not isinstance(priceDataProvider, Provider):
            raise TypeError("priceDataProvider must be a subclass of data.data_provider.Provider")

        self.algo = algo
        self.progressCallback = progressCallback
        self.context = Context(self.algo.analysis_symbols())
        self.priceDataProvider = priceDataProvider

        self.progressCounter = 0
        self.positions = []
        self.currentPosition = None
        self.priceConflation = {}

        self.algo.initialiseContext(self.context)

        for symbol in algo.analysis_symbols():
            self.priceConflation[symbol] = PriceConflator(symbol, self.algo.period(), lambda x: self.handleData(x))
            self.priceDataProvider.register(symbol)

        self.priceDataProvider.loadHistoricalData(self.algo.period() * self.algo.warmupPeriod())
        self.priceDataProvider.startPublishing(lambda symbol, tick: self.handleTickUpdate(symbol, tick))

    def handleTickUpdate(self, symbol, tick):
        try:
            logging.debug("Received tick update for %s: %s" % (symbol, tick))
            self.priceConflation[symbol].addTick(tick)
            # TODO: we need to evaluate if we have any limit orders and stop loss events triggered
        except KeyError as e:
            logging.error("Received data update for symbol we're not subscribed to")

    def handleData(self, quote):
        if quote is None or not isinstance(quote, Quote):
            raise AssertionError("Invalid quote")

        logging.debug("We have some data %s" % (quote, ))
        # self.context.addQuote(quote)
        # for position in self.context.openPositions:
        #     position.update(quote)
        # # logging.debug("Received Quote %s", quote)
        # self.algo.evaluateTickUpdate(self.context, quote)
        # if self.progressCallback is not None:
        #     self.progressCounter += 1
        #     self.progressCallback(float(self.progressCounter)/float(len(self.quotes)))

    def context(self):
        return self.context
