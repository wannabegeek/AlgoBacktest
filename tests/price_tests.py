import unittest
import datetime

from strategycontainer.symbol import Symbol
from strategycontainer.price import Tick, PriceConflator, roundDateTimeToPeriod

class PriceTest(unittest.TestCase):
    def setUp(self):
        Symbol.setDataProvider("1")
        self.callbackQuote = []

    def testTimestampRounding(self):
        t = datetime.datetime(2015, 7, 7, 13, 4, 47, 123456)
        result = roundDateTimeToPeriod(t, datetime.timedelta(seconds=5))
        self.assertEqual(datetime.datetime(2015, 7, 7, 13, 4, 45, 0), result)

        result = roundDateTimeToPeriod(t, datetime.timedelta(minutes=5))
        self.assertEqual(datetime.datetime(2015, 7, 7, 13, 0), result)

        result = roundDateTimeToPeriod(t, datetime.timedelta(hours=4))
        self.assertEqual(datetime.datetime(2015, 7, 7, 12), result)

    def callback(self, quote):
        self.callbackQuote.append(quote)

    def testQuoteConstruction(self):
        s = Symbol("TEST")
        conflator = PriceConflator("TEST", datetime.timedelta(seconds=5), self.callback)

        startTime = datetime.datetime(2015, 7, 7, 14, 10, 0)
        tick = Tick(startTime + datetime.timedelta(seconds=1), 9.0, 9.2)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=2), 8.7, 8.9)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=3), 11.0, 11.2)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=4), 10.5, 10.7)
        conflator.addTick(tick)

        tick = Tick(startTime + datetime.timedelta(seconds=5), 9.0, 9.2)
        conflator.addTick(tick)

        self.assertEqual(1, len(self.callbackQuote))
        quote = self.callbackQuote[0]
        self.assertEqual(9.1, quote.open)
        self.assertEqual(11.1, quote.high)
        self.assertEqual(8.8, quote.low)
        self.assertEqual(10.6, quote.close)

    def testQuoteConstructionOnInterval(self):
        s = Symbol("TEST")
        conflator = PriceConflator("TEST", datetime.timedelta(minutes=5), self.callback)

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
        self.assertEqual(4, quote.ticks)
        self.assertEqual(9.1, quote.open)
        self.assertEqual(11.1, quote.high)
        self.assertEqual(8.8, quote.low)
        self.assertEqual(10.6, quote.close)

    def testQuoteGap(self):
        s = Symbol("TEST")
        conflator = PriceConflator("TEST", datetime.timedelta(seconds=5), self.callback)

        startTime = datetime.datetime(2015, 7, 7, 14, 10, 0)
        tick = Tick(startTime + datetime.timedelta(seconds=1), 9.0, 9.2)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=2), 8.7, 8.9)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=3), 11.0, 11.2)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=4), 10.5, 10.7)
        conflator.addTick(tick)

        tick = Tick(startTime + datetime.timedelta(seconds=15), 9.0, 9.2)
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
