from datetime import datetime
from enum import Enum
import uuid
from backtest.symbol import Symbol
from backtest.price import Tick

class Direction(Enum):
    LONG = 0
    SHORT = 1

class Entry(object):
    class Type(Enum):
        MARKET = 0
        LIMIT = 1 # Fill below the current market price
        STOP_ENTRY = 2 # Fill above the current market price

    def __init__(self, type, price = 0.0):
        self.type = type
        self.price = price

class StopLoss(object):
    class Type(Enum):
        FIXED = 0
        TRAILING = 1

    def __init__(self, type, points):
        self.type = type
        self.points = points

class State(Enum):
    PENDING = 0
    FILLED = 1
    EXPIRED = 2
    CANCELLED = 3

class Order(object):
    def __init__(self, symbol, entry, direction, stoploss = None, takeProfit = None, expireTime = None):
        if not isinstance(symbol, Symbol):
            raise ValueError('argument "symbol" must be a Symbol')
        if not isinstance(entry, Entry):
            raise ValueError('argument "entry" must be a Entry')
        if stoploss is not None and not isinstance(stoploss, StopLoss):
            raise ValueError('argument "stoploss" must be a StopLoss')
        self.symbol = symbol
        self.entry = entry
        self.direction = direction
        self.stoploss = stoploss
        self.takeProfit = takeProfit
        self.expireTime = expireTime
        self.state = State.PENDING
        self.entryTime = datetime.utcnow()
        self.id = uuid.uuid4()

    def isPending(self):
        return self.state == State.PENDING

    def isComplete(self):
        return self.state > State.PENDING

    def shouldFill(self, tick):
        if not isinstance(tick, Tick):
            raise ValueError('argument "tick" must be a Tick')

        if self.isComplete():
            raise RunTimeError("Order is already complete")

        if self.expireTime is not None:
            timediff = datetime.utcnow() - self.entryTime
            if timediff.total_seconds() >= self.expireTime.total_seconds():
                self.state = State.EXPIRED
                return False

        if self.entry.type == Entry.Type.MARKET:
            return True
        elif self.entry.type == Entry.Type.LIMIT:
            if self.direction == Direction.LONG:
                return tick.offer <= self.entry.price
            elif self.direction == Direction.SHORT:
                return tick.bid >= self.entry.price
        elif self.entry.type == Entry.Type.STOP_ENTRY:
            if self.direction == Direction.LONG:
                return tick.offer >= self.entry.price
            elif self.direction == Direction.SHORT:
                return tick.bid <= self.entry.price

        return False