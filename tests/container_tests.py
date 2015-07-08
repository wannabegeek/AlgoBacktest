import logging
import unittest
import datetime
from data import SymbolRequestPeriod
from data.data_provider import Provider
from strategycontainer.container import Container
from strategycontainer.order import Order, Entry, Direction, State
from strategycontainer.position import Position
from strategycontainer.price import Tick
from strategycontainer.strategy import Framework
from strategycontainer.symbol import Symbol


class ContainerTestAlgo(Framework):

    def __init__(self, symbol, order):
        super(Framework, self).__init__()
        self.symbol = symbol
        self.order = order

    def portfolio_symbols(self):
        return [self.symbol, ]

    def period(self):
        return SymbolRequestPeriod.MIN_1

    def initialiseContext(self, context):
        context.__setattr__("done", False)

    def evaluateTickUpdate(self, context, quote):
        symbolContext = context.symbolContexts[quote.symbol]
        # logging.debug("I'm evaluating the data for %s" % (symbolContext, ))
        if context.__getattr__("done") is False:
            context.placeOrder(self.order)
            context.__setattr__("done", True)

class SimulatedDataProvider(Provider):
    def __init__(self, ticks):
        self.symbol = None
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

class ContainerTest(unittest.TestCase):
    def setUp(self):
        Symbol.setDataProvider("1")
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

    def testAlgoMarketOrder(self):
        symbol = Symbol('TEST')
        algo = ContainerTestAlgo(symbol, Order(symbol, 1, Entry(Entry.Type.MARKET), Direction.LONG))

        startTime = datetime.datetime(2015, 7, 7, 12)
        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(startTime, 10.0, 10.1))
        startTime = startTime + SymbolRequestPeriod.MIN_1
        ticks.append(Tick(startTime, 11.0, 11.1))
        startTime = startTime + SymbolRequestPeriod.MIN_1
        ticks.append(Tick(startTime, 12.0, 12.1))

        dataProvider = SimulatedDataProvider(ticks)

        container = Container(algo, dataProvider)
        container.start()

        self.assertEqual(1, len(container.context.orders))
        self.assertEqual(1, len(container.context.positions))
        order = container.context.orders[0]
        self.assertEqual(State.FILLED, order.state)
        position = container.context.positions[0]
        self.assertEqual(Position.ExitReason.NOT_CLOSED, position.exitReason)
        self.assertEqual(10.1, position.entryPrice)

        # logging.debug("================")
        # logging.debug("Orders:")
        # for order in container.context.orders:
        #     logging.debug("\t%s" % (order,))
        #
        # logging.debug("Positions:")
        # for position in container.context.positions:
        #     logging.debug("\t%s" % (position,))

    def testAlgoStopEntryOrder(self):
        symbol = Symbol('TEST')
        algo = ContainerTestAlgo(symbol, Order(symbol, 1, Entry(Entry.Type.STOP_ENTRY, 11.3), Direction.LONG))

        startTime = datetime.datetime(2015, 7, 7, 12)
        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(startTime, 10.0, 10.1))
        startTime = startTime + SymbolRequestPeriod.MIN_1
        ticks.append(Tick(startTime, 11.0, 11.1))
        startTime = startTime + SymbolRequestPeriod.MIN_1
        ticks.append(Tick(startTime, 12.0, 12.1))
        startTime = startTime + SymbolRequestPeriod.MIN_1
        ticks.append(Tick(startTime, 12.3, 12.4))
        startTime = startTime + SymbolRequestPeriod.MIN_1
        ticks.append(Tick(startTime, 12.8, 12.9))

        dataProvider = SimulatedDataProvider(ticks)

        container = Container(algo, dataProvider)
        container.start()

        self.assertEqual(1, len(container.context.orders))
        self.assertEqual(1, len(container.context.positions))
        order = container.context.orders[0]
        self.assertEqual(State.FILLED, order.state)
        position = container.context.positions[0]
        self.assertEqual(Position.ExitReason.NOT_CLOSED, position.exitReason)
        self.assertEqual(12.1, position.entryPrice)

        # logging.debug("================")
        # logging.debug("Orders:")
        # for order in container.context.orders:
        #     logging.debug("\t%s" % (order,))
        #
        # logging.debug("Positions:")
        # for position in container.context.positions:
        #     logging.debug("\t%s" % (position,))

    def testAlgoExpiredOrder(self):
        symbol = Symbol('TEST')
        startTime = datetime.datetime(2015, 7, 7, 12)
        algo = ContainerTestAlgo(symbol, Order(symbol, 1, Entry(Entry.Type.STOP_ENTRY, 12.5), Direction.LONG, expireTime=datetime.timedelta(seconds=90), entryTime=startTime))

        # symbol = algo.analysis_symbols()[0]
        ticks = []
        ticks.append(Tick(startTime, 10.0, 10.1))
        startTime = startTime + SymbolRequestPeriod.MIN_1
        ticks.append(Tick(startTime, 11.0, 11.1))
        startTime = startTime + SymbolRequestPeriod.MIN_1
        ticks.append(Tick(startTime, 12.0, 12.1))
        startTime = startTime + SymbolRequestPeriod.MIN_1
        ticks.append(Tick(startTime, 12.3, 12.4))
        startTime = startTime + SymbolRequestPeriod.MIN_1
        ticks.append(Tick(startTime, 12.8, 12.9))

        dataProvider = SimulatedDataProvider(ticks)

        container = Container(algo, dataProvider)
        container.start()

        self.assertEqual(1, len(container.context.orders))
        self.assertEqual(0, len(container.context.positions))
        order = container.context.orders[0]
        self.assertEqual(State.EXPIRED, order.state)

        # logging.debug("================")
        # logging.debug("Orders:")
        # for order in container.context.orders:
        #     logging.debug("\t%s" % (order,))
        #
        # logging.debug("Positions:")
        # for position in container.context.positions:
        #     logging.debug("\t%s" % (position,))