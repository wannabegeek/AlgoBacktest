import logging
import unittest
import datetime

from backtest.simulated_broker import Broker
from data.data_provider import Provider
from market.interfaces.data_provider import MarketDataPeriod
from market.order import State, Entry, Direction, Order, StopLoss
from market.position import Position
from market.price import Tick
from market.symbol import Symbol


class OrderCreator(object):
    def __init__(self, order_manager, symbol, order):
        self.order_manager = order_manager
        self.symbol = symbol
        self.order = order
        self.done = False

    def handleData(self, symbol, tick):
        if self.done is False:
            self.order_manager.placeOrder(self.order)
            self.done = True

class SimulatedDataProvider(Provider):
    def __init__(self, symbol, ticks):
        self.symbol = symbol
        self.ticks = ticks

    def register(self, symbol):
        if not isinstance(symbol, Symbol):
            raise TypeError("symbol must be a Symbol object")
        self.symbol = symbol
        pass

    def loadHistoricalData(self, period):
        pass

    def startPublishing(self, callback):
        for tick in self.ticks:
            callback(self.symbol, tick)

class OrderManagerTest(unittest.TestCase):

    def setPosition(self, position):
        self.position = position

    def setUp(self):
        Symbol.setDataProvider("1")
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
        self.position = None

    def testAlgoMarketOrder(self):
        symbol = Symbol('TEST')

        startTime = datetime.datetime(2015, 7, 7, 12)
        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(startTime, 10.0, 10.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 11.0, 11.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 12.0, 12.1))

        dataProvider = SimulatedDataProvider(symbol, ticks)
        order_manager = Broker(dataProvider)

        order = Order(symbol, 1, Entry(Entry.Type.MARKET), Direction.LONG)
        order_creator = OrderCreator(order_manager, symbol, order)
        order_manager.addPriceObserver(symbol, order_creator.handleData)

        order_manager.start()

        self.assertEqual(0, len(order_manager.orders))
        self.assertEqual(1, len(order_manager.positions))
        self.assertEqual(State.FILLED, order.state)
        position = order_manager.positions[0]
        self.assertEqual(Position.PositionStatus.OPEN, position.status)
        self.assertEqual(10.1, position.entryPrice)

    def testAlgoStopEntryOrder(self):
        symbol = Symbol('TEST')

        startTime = datetime.datetime(2015, 7, 7, 12)
        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(startTime, 10.0, 10.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 11.0, 11.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 12.0, 12.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 12.3, 12.4))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 12.8, 12.9))

        dataProvider = SimulatedDataProvider(symbol, ticks)
        order_manager = Broker(dataProvider)

        order = Order(symbol, 1, Entry(Entry.Type.STOP_ENTRY, 11.3), Direction.LONG)
        order_creator = OrderCreator(order_manager, symbol, order)
        order_manager.addPriceObserver(symbol, order_creator.handleData)

        order_manager.start()

        self.assertEqual(0, len(order_manager.orders))
        self.assertEqual(1, len(order_manager.positions))
        self.assertEqual(State.FILLED, order.state)
        position = order_manager.positions[0]
        self.assertEqual(Position.PositionStatus.OPEN, position.status)
        self.assertEqual(12.1, position.entryPrice)

    def testAlgoExpiredOrder(self):
        symbol = Symbol('TEST')
        startTime = datetime.datetime(2015, 7, 7, 12)
        order = Order(symbol, 1, Entry(Entry.Type.STOP_ENTRY, 12.5), Direction.LONG, expireTime=datetime.timedelta(seconds=90), entryTime=startTime)

        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(startTime, 10.0, 10.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 11.0, 11.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 12.0, 12.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 12.3, 12.4))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 12.8, 12.9))

        dataProvider = SimulatedDataProvider(symbol, ticks)
        order_manager = Broker(dataProvider)

        order_creator = OrderCreator(order_manager, symbol, order)
        order_manager.addPriceObserver(symbol, order_creator.handleData)

        order_manager.start()

        self.assertEqual(0, len(order_manager.orders))
        self.assertEqual(0, len(order_manager.positions))
        self.assertEqual(State.EXPIRED, order.state)

    def testStopLossMarketOrder(self):
        symbol = Symbol('TEST')
        symbol.lot_size = 1

        startTime = datetime.datetime(2015, 7, 7, 12)
        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(startTime, 10.0, 10.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 11.0, 11.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 10.0, 10.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 8.0, 8.1))

        dataProvider = SimulatedDataProvider(symbol, ticks)
        order_manager = Broker(dataProvider)

        order = Order(symbol, 1, Entry(Entry.Type.MARKET), Direction.LONG, StopLoss(StopLoss.Type.FIXED, 1))
        order_creator = OrderCreator(order_manager, symbol, order)
        order_manager.addPriceObserver(symbol, order_creator.handleData)
        order_manager.addPositionObserver(lambda position, state: self.setPosition(position))

        order_manager.start()

        self.assertEqual(0, len(order_manager.orders))
        self.assertEqual(0, len(order_manager.positions))
        self.assertEqual(State.FILLED, order.state)

        self.assertIsNotNone(self.position)
        self.assertEqual(Position.PositionStatus.STOP_LOSS, self.position.status)
        self.assertEqual(8.1, self.position.exitPrice)

    def testTakeProfitMarketOrder(self):
        symbol = Symbol('TEST')
        symbol.lot_size = 1

        startTime = datetime.datetime(2015, 7, 7, 12)
        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(startTime, 10.0, 10.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 11.0, 11.1))
        startTime = startTime + MarketDataPeriod.MIN_1
        ticks.append(Tick(startTime, 13.0, 13.1))

        dataProvider = SimulatedDataProvider(symbol, ticks)
        order_manager = Broker(dataProvider)

        order = Order(symbol, 1, Entry(Entry.Type.MARKET), Direction.LONG, takeProfit=2)
        order_creator = OrderCreator(order_manager, symbol, order)
        order_manager.addPriceObserver(symbol, order_creator.handleData)
        order_manager.addPositionObserver(lambda position, state: self.setPosition(position))

        order_manager.start()

        self.assertEqual(0, len(order_manager.orders))
        self.assertEqual(0, len(order_manager.positions))
        self.assertEqual(State.FILLED, order.state)

        self.assertIsNotNone(self.position)
        self.assertEqual(Position.PositionStatus.TAKE_PROFIT, self.position.status)
        self.assertEqual(12.0, self.position.exitPrice)