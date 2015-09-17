from datetime import datetime
import unittest
from data.dummy_symbol_provider import DummySymbolProvider

from market.order import Order, Entry, Direction, StopLoss
from market.position import Position
from market.symbol import Symbol
from market.price import Tick


class PositionExitTests(unittest.TestCase):
    def setUp(self):
        Symbol.set_info_provider("1")

    # def testStopLoss(self):
    #     s1 = Symbol("TEST")
    #     s1.lot_size = 1.0
    #
    #     # LONG
    #     order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.LONG, stoploss = StopLoss(StopLoss.Type.FIXED, 1))
    #     tick = Tick(datetime.utcnow(), 11.0, 11.1)
    #     position = Position(order, tick)
    #
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.OPEN, result)
    #     tick = Tick(datetime.utcnow(), 9.9, 10.0)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.STOP_LOSS, result)
    #     if result is not Position.PositionStatus.OPEN:
    #         position.close(tick, result)
    #
    #     self.assertEqual(10.0, position.exitPrice)
    #
    #     # SHORT
    #     order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.SHORT, stoploss = StopLoss(StopLoss.Type.FIXED, 1))
    #     tick = Tick(datetime.utcnow(), 11.0, 11.1)
    #     position = Position(order, tick)
    #
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.OPEN, result)
    #     tick = Tick(datetime.utcnow(), 12.1, 12.0)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.STOP_LOSS, result)
    #     if result is not Position.PositionStatus.OPEN:
    #         position.close(tick, result)
    #
    #     self.assertEqual(12.1, position.exitPrice)
    #
    #
    # def testStopLossWithSlippage(self):
    #     s1 = Symbol("TEST")
    #     s1.lot_size = 1.0
    #
    #     order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.LONG, stoploss = StopLoss(StopLoss.Type.FIXED, 1))
    #     tick = Tick(datetime.utcnow(), 11.0, 11.1)
    #     position = Position(order, tick)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.OPEN, result)
    #     tick = Tick(datetime.utcnow(), 8.9, 9.0)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.STOP_LOSS, result)
    #     if result is not Position.PositionStatus.OPEN:
    #         position.close(tick, result)
    #
    #     self.assertEqual(9.0, position.exitPrice)
    #
    #     order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.SHORT, stoploss = StopLoss(StopLoss.Type.FIXED, 1))
    #     tick = Tick(datetime.utcnow(), 11.0, 11.1)
    #     position = Position(order, tick)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.OPEN, result)
    #     tick = Tick(datetime.utcnow(), 13.1, 13.0)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.STOP_LOSS, result)
    #     if result is not Position.PositionStatus.OPEN:
    #         position.close(tick, result)
    #
    #     self.assertEqual(13.1, position.exitPrice)
    #
    # def testTrailingStopLoss(self):
    #     s1 = Symbol("TEST")
    #     s1.lot_size = 1.0
    #
    #     order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.LONG, stoploss = StopLoss(StopLoss.Type.TRAILING, 1))
    #     tick = Tick(datetime.utcnow(), 11.0, 11.1)
    #     position = Position(order, tick)
    #
    #     tick = Tick(datetime.utcnow(), 12.5, 12.4)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.OPEN, result)
    #
    #     tick = Tick(datetime.utcnow(), 11.8, 11.7)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.OPEN, result)
    #     tick = Tick(datetime.utcnow(), 11.5, 11.4)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.STOP_LOSS, result)
    #     if result is not Position.PositionStatus.OPEN:
    #         position.close(tick, result)
    #
    #     self.assertEqual(11.4, position.exitPrice)
    #
    # def testTakeProfit(self):
    #     s1 = Symbol("TEST")
    #     s1.lot_size = 1.0
    #
    #     # LONG
    #     order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.LONG, stoploss = None, take_profit=1.5)
    #     tick = Tick(datetime.utcnow(), 11.0, 11.1)
    #     position = Position(order, tick)
    #
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.OPEN, result)
    #     tick = Tick(datetime.utcnow(), 12.5, 12.4)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.OPEN, result)
    #
    #     tick = Tick(datetime.utcnow(), 12.4, 12.5)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.TAKE_PROFIT, result)
    #     if result is not Position.PositionStatus.OPEN:
    #         position.close(tick, result)
    #
    #     self.assertEqual(12.5, position.exitPrice)
    #
    #     # SHORT
    #     order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.SHORT, take_profit=0.5)
    #     tick = Tick(datetime.utcnow(), 10.9, 11.0)
    #     position = Position(order, tick)
    #
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.OPEN, result)
    #     tick = Tick(datetime.utcnow(), 10.5, 10.6)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.TAKE_PROFIT, result)
    #     if result is not Position.PositionStatus.OPEN:
    #         position.close(tick, result)
    #
    #     self.assertEqual(10.5, position.exitPrice)
    #
    # def testTakeProfitWithSlippage(self):
    #     s1 = Symbol("TEST")
    #     s1.lot_size = 1.0
    #
    #     # LONG
    #     order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.LONG, stoploss = None, take_profit=1.5)
    #     tick = Tick(datetime.utcnow(), 11.0, 11.1)
    #     position = Position(order, tick)
    #
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.OPEN, result)
    #     tick = Tick(datetime.utcnow(), 12.5, 12.4)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.OPEN, result)
    #
    #     tick = Tick(datetime.utcnow(), 14.4, 14.5)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.TAKE_PROFIT, result)
    #     if result is not Position.PositionStatus.OPEN:
    #         position.close(tick, result)
    #
    #     self.assertEqual(12.5, position.exitPrice)
    #
    #     # SHORT
    #     order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.SHORT, take_profit=0.5)
    #     tick = Tick(datetime.utcnow(), 10.9, 11.0)
    #     position = Position(order, tick)
    #
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.OPEN, result)
    #     tick = Tick(datetime.utcnow(), 9.5, 9.6)
    #     result = position.shouldClosePosition(tick)
    #     self.assertEqual(Position.PositionStatus.TAKE_PROFIT, result)
    #     if result is not Position.PositionStatus.OPEN:
    #         position.close(tick, result)
    #
    #     self.assertEqual(10.5, position.exitPrice)

class PositionProfitLossTests(unittest.TestCase):
    def setUp(self):
        Symbol.set_info_provider(DummySymbolProvider())

    def testLongProfit(self):
        s1 = Symbol.get("TEST")
        s1.lot_size = 10000

        # LONG
        order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.LONG)
        tick = Tick(datetime.utcnow(), 1.12239, 1.12245) # spread of 0.6
        position = Position(order, tick)

        tick = Tick(datetime.utcnow(), 1.12259, 1.12265)
        position.close(tick)

        self.assertAlmostEquals(2, position.points_delta())

    def testShortProfit(self):
        s1 = Symbol.get("TEST")
        s1.lot_size = 10000

        # LONG
        order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.SHORT)
        tick = Tick(datetime.utcnow(), 1.12239, 1.12245) # spread of 0.6
        position = Position(order, tick)

        tick = Tick(datetime.utcnow(), 1.12219, 1.12225)
        position.close(tick)

        self.assertAlmostEquals(2, position.points_delta())

    def testLongLoss(self):
        s1 = Symbol.get("TEST")
        s1.lot_size = 10000

        # LONG
        order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.LONG)
        tick = Tick(datetime.utcnow(), 1.12239, 1.12245) # spread of 0.6
        position = Position(order, tick)

        tick = Tick(datetime.utcnow(), 1.12219, 1.12225)
        position.close(tick)

        self.assertAlmostEquals(-2, position.points_delta())

    def testShortLoss(self):
        s1 = Symbol.get("TEST")
        s1.lot_size = 10000

        # LONG
        order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.SHORT)
        tick = Tick(datetime.utcnow(), 1.12239, 1.12245) # spread of 0.6
        position = Position(order, tick)

        tick = Tick(datetime.utcnow(), 1.12259, 1.12265)
        position.close(tick)

        self.assertAlmostEquals(-2, position.points_delta())

    def testModifiedStopLoss(self):
        s1 = Symbol.get("TEST")
        s1.lot_size = 10000

        # LONG
        order = Order(s1, 1, Entry(Entry.Type.MARKET), Direction.SHORT)
        tick = Tick(datetime.utcnow(), 1.12239, 1.12245) # spread of 0.6
        position = Position(order, tick)
        self.assertIsNone(position.stop_price)

        position.update(stoploss=StopLoss(StopLoss.Type.FIXED, 2))

        self.assertIsNotNone(position.stop_price)
        self.assertEqual(1.12265, position.stop_price)
