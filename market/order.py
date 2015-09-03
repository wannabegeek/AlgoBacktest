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

    def __eq__(self, other):
        return self.type == other.type and self.points == other.points

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
    class VolatileProperties(object):
        def __init__(self, quantity=None, entry=None, stoploss=None, take_profit=None, expire_time=None):
            self.quantity = quantity
            self.entry = entry
            self.stoploss = stoploss
            self.take_profit = take_profit
            self.expire_time = expire_time

    def __init__(self, symbol, quantity, entry, direction, stoploss=None, take_profit=None, expire_time=None, entry_time=datetime.utcnow()):
        if not isinstance(symbol, Symbol):
            raise ValueError('argument "symbol" must be a Symbol')
        if not isinstance(entry, Entry):
            raise ValueError('argument "entry" must be a Entry')
        if stoploss is not None and not isinstance(stoploss, StopLoss):
            raise ValueError('argument "stoploss" must be a StopLoss')

        self.version = []

        self.symbol = symbol
        self.direction = direction

        self.latest = Order.VolatileProperties(quantity, entry, stoploss, take_profit, expire_time)
        self.version.append(self.latest)

        self.state = State.PENDING_NEW
        self.entry_time = entry_time
        self.id = uuid.uuid4()
        self.context = None

    def update(self, quantity=None, entry=None, stoploss=None, take_profit=None, expire_time=None):
        if self.state is not State.PENDING_NEW:
            self.state = State.PENDING_MODIFY

        quantity = quantity if quantity else self.latest.quantity
        entry = entry if entry else self.latest.entry
        stoploss = stoploss if stoploss else self.latest.stoploss
        take_profit = take_profit if take_profit else self.latest.take_profit
        expire_time = expire_time if expire_time else self.latest.expire_time

        self.latest = Order.VolatileProperties(quantity, entry, stoploss, take_profit, expire_time)
        self.version.append(self.latest)

    def cancel(self):
        self.state = State.PENDING_CANCEL

    @property
    def quantity(self):
        return self.latest.quantity

    @property
    def entry(self):
        return self.latest.entry

    @property
    def stoploss(self):
        return self.latest.stoploss

    @property
    def take_profit(self):
        return self.latest.take_profit

    @property
    def expire_time(self):
        return self.latest.expire_time

    def is_pending(self):
        return self.state.value <= State.WORKING.value

    def is_complete(self):
        return self.state.value > State.WORKING.value

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return "%s: %s %s@%s" % (self.state.name, self.direction.name, self.latest.quantity, "MARKET" if self.latest.entry.type == Entry.Type.MARKET else self.latest.entry.price)

    __repr__ = __str__