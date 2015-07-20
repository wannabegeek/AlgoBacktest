import logging
import threading
from queue import Queue

from market.market_data import MarketData, PriceConflator
from market.orderbook import OrderBook, MultiThreadedOrderBook
from market.price import Quote
from strategy.strategy import Framework, Context
from market.symbol import Symbol


class Container(object):
    def __init__(self, algo, order_book, data_provider):
        if not isinstance(algo, Framework):
            raise TypeError("algorithm must be a subclass of strategy.strategy.Framework")
        if not isinstance(order_book, OrderBook):
            raise TypeError("order_book must be a subclass of OrderBook")
        if not isinstance(data_provider, MarketData):
            raise TypeError("data_provider must be a subclass of MarketData")

        Symbol.setDataProvider("")

        self.algo = algo
        self.order_book = order_book
        self.data_provider = data_provider
        self.context = Context(self.order_book, self.algo.analysis_symbols(), self.algo.warmupPeriod())

        self.algo.initialiseContext(self.context)

        self.order_book.addOrderStatusObserver(self.context, self.orderStatusObserver)
        self.order_book.addPositionStatusObserver(self.context, self.positionStatusObserver)

        for symbol in self.algo.analysis_symbols():
            self.data_provider.addPriceObserver(symbol, self.algo.period(), self.handleTickUpdate)

    def handleTickUpdate(self, symbol, quote):
        """
        This method gets called from the MarketData framework
        """
        if quote is None or not isinstance(quote, Quote):
            raise TypeError("Invalid quote")

        self.context.addQuote(quote)
        self.algo.evaluateTickUpdate(self.context, quote)

    def orderStatusObserver(self, order, previousState):
        logging.debug("Received order status update =================")

    def positionStatusObserver(self, position, previousState):
        if previousState is None:
            self.context.positions.append(position)

    def context(self):
        return self.context

    def __str__(self):
        totalPositions = len(list(filter(lambda x: not x.isOpen(), self.context.positions)))

        if totalPositions == 0:
            return "========================\nAlgo %s\nNo Positions taken" % (self.algo.identifier(),)
        else:
            closed = list(map(lambda x: "%s  --> %.2fpts (%s)" % (x, x.pointsDelta(), x.positionTime()), filter(lambda x: not x.isOpen(), self.context.positions)))
            open = list(map(lambda x: "%s" % (x), filter(lambda x: x.isOpen(), self.context.positions)))
            winning = list(filter(lambda x: x.pointsDelta() > 0.0, filter(lambda x: not x.isOpen(), self.context.positions)))

            return "========================\nAlgo %s\nCompleted:\n%s\nOpen:\n%s\nWinning Ratio: %.2f%%\nTotal Pts: %.2f" % (self.algo.identifier(), "\n".join(closed),
                                                                       "\n".join(open),
                                                                       (len(winning)/totalPositions * 100),
                                                                       sum([x.pointsDelta() for x in filter(lambda x: not x.isOpen(), self.context.positions)]))


class MultiThreadedContainer(object):
    def __init__(self, algo, order_book, data_provider):
        if not isinstance(algo, Framework):
            raise TypeError("algorithm must be a subclass of strategy.strategy.Framework")
        if not isinstance(order_book, MultiThreadedOrderBook):
            raise TypeError("order_book must be a subclass of MultiThreadedOrderBook")
        if not isinstance(data_provider, MarketData):
            raise TypeError("data_provider must be a subclass of MarketData")

        Symbol.setDataProvider("")

        self.algo = algo
        self.order_book = order_book
        self.data_provider = data_provider
        self.context = Context(self.order_book, self.algo.analysis_symbols())

        self.queue = Queue()

        self.algo.initialiseContext(self.context)

        for symbol in self.algo.analysis_symbols():
            self.data_provider.addPriceObserver(symbol, self.algo.period(), self.handleTickUpdate)

    def handleTickUpdate(self, symbol, quote):
        """
        This method gets called from the MarketData framework
        """
        if quote is None or not isinstance(quote, Quote):
            raise TypeError("Invalid quote")

        self.queue.put(quote, True)

    def start(self):
        t = threading.Thread(target=self.mainloop)
        t.setDaemon(True)
        t.start()

    def mainloop(self):
        while True:
            quote = self.queue.get(True)
            logging.debug("Handling quote data: %s" % (quote,))
            self.context.addQuote(quote)
            self.algo.evaluateTickUpdate(self.context, quote)

    def context(self):
        return self.context
