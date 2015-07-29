from enum import Enum
import uuid

from market.order import Direction, State, Order
from market.price import Tick


class Position(object):
    class PositionStatus(Enum):
        OPEN = 0
        CLOSED = 1
        STOP_LOSS = 2
        TAKE_PROFIT = 3

    def __init__(self, order, tick):
        if not isinstance(order, Order):
            raise ValueError('argument "order" must be a Order')
        if not isinstance(tick, Tick):
            raise ValueError('argument "tick" must be a Tick')

        self.order = order
        self.order.state = State.FILLED # mark the order as filled

        self.entry_tick = tick
        self.entry_price = tick.offer if self.order.direction == Direction.LONG else tick.bid
        self.exit_tick = None
        self.exit_price = None

        self.closed = False
        self.id = uuid.uuid4()
        self.status = Position.PositionStatus.OPEN
        if self.order.stoploss is not None:
            if self.order.direction == Direction.LONG:
                self.stop_price = tick.bid - self.order.stoploss.points / self.order.symbol.lot_size
            else:
                self.stop_price = tick.offer + self.order.stoploss.points / self.order.symbol.lot_size
        else:
            self.stop_price = None

        if self.order.take_profit is not None:
            if self.order.direction == Direction.LONG:
                self.take_profit = tick.offer + self.order.take_profit / self.order.symbol.lot_size
            else:
                self.take_profit = tick.bid - self.order.take_profit / self.order.symbol.lot_size
        else:
            self.take_profit = None


    def is_open(self):
        return not self.closed

    def close(self, tick, reason = PositionStatus.CLOSED):
        if reason == Position.PositionStatus.TAKE_PROFIT:
            self.exit_price = self.take_profit
        else:
            if self.order.direction == Direction.LONG:
                self.exit_price = tick.offer
            else:
                self.exit_price = tick.bid

        self.exit_tick = tick
        self.closed = True
        self.status = reason

    def points_delta(self):
        if self.status == Position.PositionStatus.OPEN:
            raise ValueError("Position is still open")

        price_delta = 0.0
        if self.order.direction == Direction.LONG:
            price_delta = self.exit_price - self.entry_price
        else:
            price_delta = self.entry_price - self.exit_price

        return price_delta * self.order.symbol.lot_size

    def equity(self):
        return self.points_delta() * self.order.quantity

    def position_time(self):
        if self.status == Position.PositionStatus.OPEN:
            raise ValueError("Position is still open")
        return self.exit_tick.timestamp - self.entry_tick.timestamp

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return "%s: %-11s [%-5s %.6s --> %.6s]" % (self.id, self.status.name, self.order.direction.name, self.entry_price, "OPEN" if self.status == Position.PositionStatus.OPEN else self.exit_price)

    __repr__ = __str__