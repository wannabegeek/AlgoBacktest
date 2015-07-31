import unittest
import datetime
from data.dummy_symbol_provider import DummySymbolProvider
from market.market_data import MarketDataPeriod, PriceConflator
from market.price import Tick

from market.symbol import Symbol


class PriceTest(unittest.TestCase):
    def setUp(self):
        Symbol.set_info_provider(DummySymbolProvider())
        self.callbackQuote = []

    def testTimestampRounding(self):

        t = 1437832541.348046
        result = PriceConflator.round_datetime_to_period(t, 5.0)
        self.assertEqual(1437832540, result)

        result = PriceConflator.round_datetime_to_period(t, 300.0)  # 5 mins
        self.assertEqual(1437832500, result)

        result = PriceConflator.round_datetime_to_period(t, 14400.0)  # 4 hours
        self.assertEqual(1437825600, result)

    def callback(self, quote):
        self.callbackQuote.append(quote)

    def testQuoteConstruction(self):
        s = Symbol.get("TEST")
        conflator = PriceConflator("TEST", MarketDataPeriod.MIN_5, self.callback)

        start_time = datetime.datetime(2015, 7, 7, 14, 10, 0)
        start_time = start_time + MarketDataPeriod.MIN_1
        tick = Tick(start_time.timestamp(), 9.0, 9.2)  # 14:11:00
        conflator.add_tick(tick)
        start_time = start_time + MarketDataPeriod.MIN_1
        tick = Tick(start_time.timestamp(), 8.7, 8.9)  # 14:12:00
        conflator.add_tick(tick)
        start_time = start_time + MarketDataPeriod.MIN_1
        tick = Tick(start_time.timestamp(), 11.0, 11.2)  # 14:13:00
        conflator.add_tick(tick)
        start_time = start_time + MarketDataPeriod.MIN_1
        tick = Tick(start_time.timestamp(), 10.5, 10.7)  # 14:14:00
        conflator.add_tick(tick)

        start_time = start_time + MarketDataPeriod.MIN_1
        tick = Tick(start_time.timestamp(), 9.0, 9.2)  # 14:15:00
        conflator.add_tick(tick)

        self.assertEqual(1, len(self.callbackQuote))
        quote = self.callbackQuote[0]
        self.assertEqual(9.1, quote.open)
        self.assertEqual(11.1, quote.high)
        self.assertEqual(8.8, quote.low)
        self.assertEqual(10.6, quote.close)

    def testQuoteConstructionOnInterval(self):
        s = Symbol.get("TEST")
        conflator = PriceConflator("TEST", MarketDataPeriod.MIN_5, self.callback)

        start_time = datetime.datetime(2015, 7, 7, 14, 0, 0)
        tick = Tick(start_time.timestamp(), 9.0, 9.2)
        conflator.add_tick(tick)
        tick = Tick((start_time + datetime.timedelta(seconds=60)).timestamp(), 9.0, 9.2)
        conflator.add_tick(tick)
        tick = Tick((start_time + datetime.timedelta(seconds=120)).timestamp(), 8.7, 8.9)
        conflator.add_tick(tick)
        tick = Tick((start_time + datetime.timedelta(seconds=180)).timestamp(), 11.0, 11.2)
        conflator.add_tick(tick)
        tick = Tick((start_time + datetime.timedelta(seconds=240)).timestamp(), 10.5, 10.7)
        conflator.add_tick(tick)
        tick = Tick((start_time + datetime.timedelta(seconds=300)).timestamp(), 9.0, 9.2)
        conflator.add_tick(tick)
        tick = Tick((start_time + datetime.timedelta(seconds=360)).timestamp(), 9.0, 9.2)
        conflator.add_tick(tick)

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

        start_time = datetime.datetime(2015, 7, 7, 14, 10, 0)
        start_time = start_time + MarketDataPeriod.MIN_1
        tick = Tick(start_time.timestamp(), 9.0, 9.2)  # 14:11
        conflator.add_tick(tick)
        start_time = start_time + MarketDataPeriod.MIN_1
        tick = Tick(start_time.timestamp(), 8.7, 8.9)  # 14:12
        conflator.add_tick(tick)
        start_time = start_time + MarketDataPeriod.MIN_1
        tick = Tick(start_time.timestamp(), 11.0, 11.2)  # 14:13
        conflator.add_tick(tick)
        start_time = start_time + MarketDataPeriod.MIN_1
        tick = Tick(start_time.timestamp(), 10.5, 10.7)  # 14:14
        conflator.add_tick(tick)

        self.assertEqual(0, len(self.callbackQuote))  # (All in 14:10:00)

        start_time = start_time + MarketDataPeriod.MIN_15
        tick = Tick(start_time.timestamp(), 9.0, 9.2)  # 14:29
        conflator.add_tick(tick)

        self.assertEqual(3, len(self.callbackQuote))  # 14:15:00, 14:20:00, 14:25:00

        start_time = start_time + MarketDataPeriod.MIN_1
        tick = Tick(start_time.timestamp(), 10.5, 10.7)  # 14:30
        conflator.add_tick(tick)

        self.assertEqual(4, len(self.callbackQuote))
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
