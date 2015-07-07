import unittest
import datetime
from backtest.symbol import Symbol
from backtest.price import Tick, PriceConflator, Quote

class PriceTest(unittest.TestCase):
    def setUp(self):
        Symbol.setDataProvider("1")
        self.callbackQuote = []

    def testTimestampRounding(self):
        t = datetime.datetime(2015, 7, 7, 13, 4, 47, 123456)
        result = PriceConflator._roundDateTimeToPeriod(t, datetime.timedelta(seconds=5))
        self.assertEqual(datetime.datetime(2015, 7, 7, 13, 4, 45, 0), result)

        result = PriceConflator._roundDateTimeToPeriod(t, datetime.timedelta(minutes=5))
        self.assertEqual(datetime.datetime(2015, 7, 7, 13, 0), result)

        result = PriceConflator._roundDateTimeToPeriod(t, datetime.timedelta(hours=4))
        self.assertEqual(datetime.datetime(2015, 7, 7, 12), result)

    def callback(self, quote):
        self.callbackQuote.append(quote)

    def testMarketOrder(self):
        s = Symbol("TEST")
        conflator = PriceConflator("TEST", datetime.timedelta(seconds=5), self.callback)

        startTime = datetime.datetime.utcnow()
        tick = Tick(startTime, 11.0, 11.1)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=1), 9.0, 9.2)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=2), 8.7, 8.9)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=4), 11.0, 11.2)
        conflator.addTick(tick)
        tick = Tick(startTime + datetime.timedelta(seconds=5), 10.5, 10.7)
        conflator.addTick(tick)

        self.assertEqual(1, len(self.callbackQuote))
        self.assertEqual(9.1, self.callbackQuote.open)
        self.assertEqual(11.1, self.callbackQuote.high)
        self.assertEqual(8.8, self.callbackQuote.low)
        self.assertEqual(10.5, self.callbackQuote.close)

