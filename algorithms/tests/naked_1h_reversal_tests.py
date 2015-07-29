import unittest
import datetime
from algorithms.naked_1h_reversal import NakedReversalAlgo
from data.dummy_symbol_provider import DummySymbolProvider
from market.interfaces.orderrouter import OrderRouter
from market.market_data import MarketDataPeriod
from market.orderbook import OrderBook
from market.price import Quote, Tick

from market.symbol import Symbol
from strategy.strategy import Context

class TestOrderRouter(OrderRouter):
    def place_order(self, order):
        print("Placed order")

    def cancel_order(self, order):
        pass

    def close_position(self, position):
        pass

    def modify_order(self, order):
        pass


class NakedTests(unittest.TestCase):
    def setUp(self):
        Symbol.setDataProvider(DummySymbolProvider())
        self.order_router = TestOrderRouter()
        self.algo = NakedReversalAlgo(10, 50, 100)
        self.context = Context(10000, OrderBook(self.order_router), self.algo.analysis_symbols(), self.algo.warmupPeriod())

    def testBuyEntry(self):
        symbol = self.algo.analysis_symbols()[0]
        start_time = datetime.datetime(2015, 7, 15, 12, 0, 0)
        quotes = []

        ticks = ((0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2),
                 (0.2, 0.3, 0.1, 0.2))

        for t in ticks:
            tick = Tick(start_time.timestamp(), t[0], t[0])
            quote = Quote(symbol, start_time, MarketDataPeriod.HOUR_1 - datetime.timedelta(seconds=1), tick)
            quote.add_tick(Tick(start_time.timestamp(), t[1], t[1]))
            quote.add_tick(Tick(start_time.timestamp(), t[2], t[2]))
            quote.add_tick(Tick(start_time.timestamp(), t[3], t[3]))
            quotes.append(quote)
            start_time += MarketDataPeriod.HOUR_1


        for quote in quotes:
            self.context.addQuote(quote)
            self.algo.evaluateTickUpdate(self.context, quote)

        # self.assertEqual(s1, s2)
        # self.assertEqual(id(s1.__dict__), id(s2.__dict__))
