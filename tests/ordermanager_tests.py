import logging
import unittest
import datetime

from backtest.simulated_broker import Broker
from data.dummy_symbol_provider import DummySymbolProvider
from data.interfaces.data_provider import Provider
from market.market_data import MarketDataPeriod
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

    def handle_data(self, symbol, tick):
        if self.done is False:
            self.order_manager.place_order(self.order)
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

    def load_historical_data(self, period):
        pass

    def start_publishing(self, callback):
        for tick in self.ticks:
            callback(self.symbol, tick)

class OrderManagerTest(unittest.TestCase):

    def setPosition(self, position):
        self.position = position

    def setUp(self):
        Symbol.set_info_provider(DummySymbolProvider())
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
        self.position = None

    def testAlgoMarketOrder(self):
        symbol = Symbol.get('TEST')

        start_time = datetime.datetime(2015, 7, 7, 12)
        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(start_time, 10.0, 10.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 11.0, 11.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 12.0, 12.1))

        dataProvider = SimulatedDataProvider(symbol, ticks)
        order_manager = Broker(dataProvider)
        order_manager.subscribeSymbol(symbol)

        order = Order(symbol, 1, Entry(Entry.Type.MARKET), Direction.LONG)
        order_creator = OrderCreator(order_manager, symbol, order)
        order_manager.addPriceObserver(order_creator.handle_data)

        order_manager.start()

        self.assertEqual(0, len(order_manager.orders))
        self.assertEqual(1, len(order_manager.positions))
        self.assertEqual(State.FILLED, order.state)
        position = order_manager.positions[0]
        self.assertEqual(Position.PositionStatus.OPEN, position.status)
        self.assertEqual(10.1, position.entry_price)

    def testAlgoStopEntryOrder(self):
        symbol = Symbol.get('TEST')

        start_time = datetime.datetime(2015, 7, 7, 12)
        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(start_time, 10.0, 10.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 11.0, 11.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 12.0, 12.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 12.3, 12.4))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 12.8, 12.9))

        dataProvider = SimulatedDataProvider(symbol, ticks)
        order_manager = Broker(dataProvider)
        order_manager.subscribeSymbol(symbol)

        order = Order(symbol, 1, Entry(Entry.Type.STOP_ENTRY, 11.3), Direction.LONG)
        order_creator = OrderCreator(order_manager, symbol, order)
        order_manager.addPriceObserver(order_creator.handle_data)

        order_manager.start()

        self.assertEqual(0, len(order_manager.orders))
        self.assertEqual(1, len(order_manager.positions))
        self.assertEqual(State.FILLED, order.state)
        position = order_manager.positions[0]
        self.assertEqual(Position.PositionStatus.OPEN, position.status)
        self.assertEqual(12.1, position.entry_price)

    def testAlgoExpiredOrder(self):
        symbol = Symbol.get('TEST')
        start_time = datetime.datetime(2015, 7, 7, 12)
        order = Order(symbol, 1, Entry(Entry.Type.STOP_ENTRY, 12.5), Direction.LONG, expire_time=datetime.timedelta(seconds=90), entry_time=start_time)

        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(start_time, 10.0, 10.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 11.0, 11.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 12.0, 12.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 12.3, 12.4))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 12.8, 12.9))

        dataProvider = SimulatedDataProvider(symbol, ticks)
        order_manager = Broker(dataProvider)
        order_manager.subscribeSymbol(symbol)

        order_creator = OrderCreator(order_manager, symbol, order)
        order_manager.addPriceObserver(order_creator.handle_data)

        order_manager.start()

        self.assertEqual(0, len(order_manager.orders))
        self.assertEqual(0, len(order_manager.positions))
        self.assertEqual(State.EXPIRED, order.state)

    def testStopLossMarketOrder(self):
        symbol = Symbol.get('TEST')
        symbol.lot_size = 1

        start_time = datetime.datetime(2015, 7, 7, 12)
        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(start_time, 10.0, 10.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 11.0, 11.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 10.0, 10.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 8.0, 8.1))

        dataProvider = SimulatedDataProvider(symbol, ticks)
        order_manager = Broker(dataProvider)
        order_manager.subscribeSymbol(symbol)

        order = Order(symbol, 1, Entry(Entry.Type.MARKET), Direction.LONG, StopLoss(StopLoss.Type.FIXED, 1))
        order_creator = OrderCreator(order_manager, symbol, order)
        order_manager.addPriceObserver(order_creator.handle_data)
        order_manager.addPositionObserver(lambda position, state: self.setPosition(position))

        order_manager.start()

        self.assertEqual(0, len(order_manager.orders))
        self.assertEqual(0, len(order_manager.positions))
        self.assertEqual(State.FILLED, order.state)

        self.assertIsNotNone(self.position)
        self.assertEqual(Position.PositionStatus.STOP_LOSS, self.position.status)
        self.assertEqual(8.1, self.position.exit_price)

    def testTakeProfitMarketOrder(self):
        symbol = Symbol.get('TEST')
        symbol.lot_size = 1

        start_time = datetime.datetime(2015, 7, 7, 12)
        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(start_time, 10.0, 10.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 11.0, 11.1))
        start_time = start_time + MarketDataPeriod.MIN_1
        ticks.append(Tick(start_time, 13.0, 13.1))

        dataProvider = SimulatedDataProvider(symbol, ticks)
        order_manager = Broker(dataProvider)
        order_manager.subscribeSymbol(symbol)

        order = Order(symbol, 1, Entry(Entry.Type.MARKET), Direction.LONG, take_profit=2)
        order_creator = OrderCreator(order_manager, symbol, order)
        order_manager.addPriceObserver(order_creator.handle_data)
        order_manager.addPositionObserver(lambda position, state: self.setPosition(position))

        order_manager.start()

        self.assertEqual(0, len(order_manager.orders))
        self.assertEqual(0, len(order_manager.positions))
        self.assertEqual(State.FILLED, order.state)

        self.assertIsNotNone(self.position)
        self.assertEqual(Position.PositionStatus.TAKE_PROFIT, self.position.status)
        self.assertEqual(12.1, self.position.exit_price)
        self.assertAlmostEquals(2.0, self.position.points_delta())