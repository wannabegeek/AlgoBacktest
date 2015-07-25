import unittest
import datetime
from data.dummy_symbol_provider import DummySymbolProvider
from market.market_data import MarketDataPeriod, roundDateTimeToPeriod, PriceConflator
from market.price import Tick

from market.symbol import Symbol


class PriceTest(unittest.TestCase):
    def setUp(self):
        Symbol.setDataProvider(DummySymbolProvider())
        self.callbackQuote = []

    def testTimestampRounding(self):

        t = 1437832541.348046
        result = roundDateTimeToPeriod(t, datetime.timedelta(seconds=5))
        self.assertEqual(1437832540, result)

        result = roundDateTimeToPeriod(t, datetime.timedelta(minutes=5))
        self.assertEqual(1437832500, result)

        result = roundDateTimeToPeriod(t, datetime.timedelta(hours=4))
        self.assertEqual(1437825600, result)

    def callback(self, quote):
        self.callbackQuote.append(quote)

    def testQuoteConstruction(self):
        s = Symbol.get("TEST")
        conflator = PriceConflator("TEST", MarketDataPeriod.MIN_5, self.callback)

        startTime = datetime.datetime(2015, 7, 7, 14, 10, 0)
        startTime = startTime + MarketDataPeriod.MIN_1
        tick = Tick(startTime, 9.0, 9.2)
        conflator.addTick(tick)
        startTime = startTime + MarketDataPeriod.MIN_1
        tick = Tick(startTime, 8.7, 8.9)
        conflator.addTick(tick)
        startTime = startTime + MarketDataPeriod.MIN_1
        tick = Tick(startTime, 11.0, 11.2)
        conflator.addTick(tick)
        startTime = startTime + MarketDataPeriod.MIN_1
        tick = Tick(startTime, 10.5, 10.7)
        conflator.addTick(tick)

        startTime = startTime + MarketDataPeriod.MIN_1
        tick = Tick(startTime, 9.0, 9.2)
        conflator.addTick(tick)

        self.assertEqual(1, len(self.callbackQuote))
        quote = self.callbackQuote[0]
        self.assertEqual(9.1, quote.open)
        self.assertEqual(11.1, quote.high)
        self.assertEqual(8.8, quote.low)
        self.assertEqual(10.6, quote.close)

    def testQuoteConstructionOnInterval(self):
        s = Symbol.get("TEST")
        conflator = PriceConflator("TEST", MarketDataPeriod.MIN_5, self.callback)

        startTime = datetime.datetime(2015, 7, 7, 14, 0, 0)
        tick = Tick(startTime, 9.0, 9.2)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=60), 9.0, 9.2)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=120), 8.7, 8.9)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=180), 11.0, 11.2)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=240), 10.5, 10.7)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=300), 9.0, 9.2)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=360), 9.0, 9.2)
        conflator.addTick(tick)

        self.assertEqual(1, len(self.callbackQuote))
        quote = self.callbackQuote[0]
        self.assertEqual(5, quote.ticks)
        self.assertEqual(9.1, quote.open)
        self.assertEqual(11.1, quote.high)
        self.assertEqual(8.8, quote.low)
        self.assertEqual(10.6, quote.close)

    def testQuoteGap(self):
        s = Symbol.get("TEST")
        conflator = PriceConflator("TEST", MarketDataPeriod.MIN_5, self.callback)

        startTime = datetime.datetime(2015, 7, 7, 14, 10, 0)
        startTime = startTime + MarketDataPeriod.MIN_1
        tick = Tick(startTime, 9.0, 9.2)
        conflator.addTick(tick)
        startTime = startTime + MarketDataPeriod.MIN_1
        tick = Tick(startTime, 8.7, 8.9)
        conflator.addTick(tick)
        startTime = startTime + MarketDataPeriod.MIN_1
        tick = Tick(startTime, 11.0, 11.2)
        conflator.addTick(tick)
        startTime = startTime + MarketDataPeriod.MIN_1
        tick = Tick(startTime, 10.5, 10.7)
        conflator.addTick(tick)

        startTime = startTime + MarketDataPeriod.MIN_15
        tick = Tick(startTime, 9.0, 9.2)
        conflator.addTick(tick)

        self.assertEqual(3, len(self.callbackQuote))
        quote = self.callbackQuote[0]
        self.assertEqual(9.1, quote.open)
        self.assertEqual(11.1, quote.high)
        self.assertEqual(8.8, quote.low)
        self.assertEqual(10.6, quote.close)

        quote = self.callbackQuote[1]
        self.assertEqual(10.6, quote.open)
        self.assertEqual(10.6, quote.high)
        self.assertEqual(10.6, quote.low)
        self.assertEqual(10.6, quote.close)
