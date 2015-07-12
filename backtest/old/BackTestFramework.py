import logging
from algorithms.sample_algorithm import Algo
from strategy.strategy import Framework, Context


class BackTestFramework(object):
    algo = None
    dataProviders = []
    quotes = []
    context = None

    def __init__(self, algo, dataProviderClass, progressCallback = None):
        if not isinstance(algo, Framework):
            raise TypeError("algorithm must be a subclass of strategy.strategy.Framework")

        self.algo = algo
        self.progressCounter = 0
        self.progressCallback = progressCallback
        self.context = Context(self.algo.analysis_symbols())

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

def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    client = BackTestFramework(Algo(), None)
    logging.info("All done... shutting down")

if __name__ == '__main__':
    main()