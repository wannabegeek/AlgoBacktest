from enum import Enum

class Direction(Enum):
    LONG = 0
    SHORT = 1

class Entry(object):
    class Type(Enum):
        Market = 0
        Limit = 1
        StopEntry = 2

    def __init__(self, type, price = 0.0):
        self.type = type
        self.price = price

class StopLoss(object):
    class Type(Enum):
        Fixed = 0
        Trailing = 1

    def __init__(self, type, price):
        self.type = type
        self.price = price

class State(Enum):
    PENDING = 0
    ACTIVE = 1
    CANCELLED = 2

class Order(object):
    def __init__(self, symbol, entry, direction, stoploss, takeProfit = None):
        self.symbol = symbol
        self.entry = entry
        self.direction = direction
        self.stoploss = stoploss
        self.takeProfit = takeProfit
        self.state = State.PENDING

    def setState(self, state):
        self.state = state

