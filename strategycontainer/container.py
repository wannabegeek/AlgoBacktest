import logging
from strategycontainer.ordermanager import OrderManager
from strategycontainer.price import PriceConflator, Quote
from strategycontainer.strategy import Framework, Context
from strategycontainer.symbol import Symbol


class Container(object):
    def __init__(self, algo, order_manager):
        if not isinstance(algo, Framework):
            raise TypeError("algorithm must be a subclass of strategycontainer.strategy.Framework")
        if not isinstance(order_manager, OrderManager):
            raise TypeError("order_manager must be a subclass of OrderManager")

        Symbol.setDataProvider("")

        self.algo = algo
        self.order_manager = order_manager
        self.context = Context(self.order_manager, self.algo.analysis_symbols())

        self.progressCounter = 0
        self.priceConflation = {}

        self.algo.initialiseContext(self.context)

    def start(self):
        for symbol in self.algo.analysis_symbols():
            self.priceConflation[symbol] = PriceConflator(symbol, self.algo.period(), lambda x: self.handleData(x))
            self.order_manager.addPriceObserver(symbol, self.handleTickUpdate)

        self.order_manager.start()

    def handleTickUpdate(self, symbol, tick):
        try:
            self.priceConflation[symbol].addTick(tick)
        except KeyError as e:
            logging.error("Received data update for symbol we're not subscribed to (%s)" % (symbol,))

    def handleData(self, quote):
        """
        This method gets called from the PriceConflator callback
        """
        if quote is None or not isinstance(quote, Quote):
            raise TypeError("Invalid quote")

        logging.debug("Handling quote data: %s" % (quote,))
        self.context.addQuote(quote)
        self.algo.evaluateTickUpdate(self.context, quote)

    def context(self):
        return self.context
