from datetime import datetime
from enum import Enum
import uuid

from market.symbol import Symbol


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
    PENDING_NEW = 0
    PENDING_MODIFY = 1
    PENDING_CANCEL = 2
    WORKING = 10
    REJECTED = 20
    FILLED = 21
    EXPIRED = 22
    CANCELLED = 23

class Order(object):
    def __init__(self, symbol, quantity, entry, direction, stoploss = None, take_profit = None, expire_time = None, entry_time = datetime.utcnow()):
        if not isinstance(symbol, Symbol):
            raise ValueError('argument "symbol" must be a Symbol')
        if not isinstance(entry, Entry):
            raise ValueError('argument "entry" must be a Entry')
        if stoploss is not None and not isinstance(stoploss, StopLoss):
            raise ValueError('argument "stoploss" must be a StopLoss')
        self.symbol = symbol
        self.quantity = quantity
        self.entry = entry
        self.direction = direction
        self.stoploss = stoploss
        self.take_profit = take_profit
        self.expire_time = expire_time
        self.state = State.PENDING_NEW
        self.entry_time = entry_time
        self.id = uuid.uuid4()
        self.context = None

    def is_pending(self):
        return self.state.value <= State.WORKING.value

    def is_complete(self):
        return self.state.value > State.WORKING.value

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return "%s: %s %s@%s" % (self.state.name, self.direction.name, self.quantity, "MARKET" if self.entry.type == Entry.Type.MARKET else self.entry.price)

    __repr__ = __str__