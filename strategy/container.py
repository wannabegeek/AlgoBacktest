import logging
from market.interfaces.data_provider import DataProvider

from market.interfaces.orderrouter import OrderRouter
from market.market_data import MarketData
from market.price import PriceConflator, Quote
from strategy.strategy import Framework, Context
from market.symbol import Symbol


class Container(object):
    def __init__(self, algo, order_manager, data_provider):
        if not isinstance(algo, Framework):
            raise TypeError("algorithm must be a subclass of strategy.strategy.Framework")
        if not isinstance(order_manager, OrderRouter):
            raise TypeError("order_manager must be a subclass of OrderManager")
        if not isinstance(data_provider, MarketData):
            raise TypeError("data_provider must be a subclass of MarketData")

        Symbol.setDataProvider("")

        self.algo = algo
        self.order_manager = order_manager
        self.data_provider = data_provider
        self.context = Context(self.order_manager, self.algo.analysis_symbols())

        self.progressCounter = 0
        self.priceConflation = {}

        self.algo.initialiseContext(self.context)

        for symbol in self.algo.analysis_symbols():
            self.priceConflation[symbol] = PriceConflator(symbol, self.algo.period(), lambda x: self.handleData(x))
            self.data_provider.addPriceObserver(symbol, self.algo.period(), self.handleTickUpdate)

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
