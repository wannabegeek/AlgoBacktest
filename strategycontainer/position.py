from enum import Enum
import logging
import uuid

from strategycontainer.order import StopLoss, Direction, State, Order
from strategycontainer.price import Tick


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

        self.entryPrice = tick.offer if self.order.direction == Direction.LONG else tick.bid
        self.exitTick = None
        self.closed = False
        self.id = uuid.uuid4()
        self.status = Position.PositionStatus.OPEN
        self.exitPrice = None
        if self.order.stoploss is not None:
            if self.order.direction == Direction.LONG:
                self.stopPrice = tick.bid - self.order.stoploss.points / self.order.symbol.lot_size
            else:
                self.stopPrice = tick.offer + self.order.stoploss.points / self.order.symbol.lot_size
        else:
            self.stopPrice = None

        if self.order.takeProfit is not None:
            if self.order.direction == Direction.LONG:
                self.takeProfit = tick.bid + self.order.takeProfit / self.order.symbol.lot_size
            else:
                self.takeProfit = tick.offer - self.order.takeProfit / self.order.symbol.lot_size
        else:
            self.takeProfit = None


    def isOpen(self):
        return not self.closed

    def close(self, tick, reason = PositionStatus.CLOSED):
        if reason == Position.PositionStatus.TAKE_PROFIT:
            self.exitPrice = self.takeProfit
        else:
            if self.order.direction == Direction.LONG:
                self.exitPrice = tick.offer
            else:
                self.exitPrice = tick.bid

        self.exitTick = tick
        self.closed = True
        self.status = reason

    def pointsDelta(self):
        priceDelta = 0.0
        if self.order.direction == Direction.LONG:
            priceDelta = self.exitPrice - self.entryPrice
        else:
            priceDelta = self.entryPrice - self.exitPrice

        return priceDelta * self.order.symbol.lot_size

    def shouldClosePosition(self, tick):
        if self.isOpen():
            if self.order.stoploss is not None:
                if self.order.stoploss.type == StopLoss.Type.TRAILING:
                    if self.order.direction == Direction.LONG:
                        self.stopPrice = max(self.stopPrice, tick.bid - self.order.stoploss.points * self.order.symbol.lot_size)
                    else:
                        self.stopPrice = min(self.stopPrice, tick.offer + self.order.stoploss.points * self.order.symbol.lot_size)

                if self.order.direction == Direction.LONG:
                    if tick.offer <= self.stopPrice:
                        # logging.debug("Position %s hit its stop loss (tick %s)" % (self, tick))
                        self.status = Position.PositionStatus.STOP_LOSS
                        self.exitPrice = tick.offer
                else:
                    if tick.bid >= self.stopPrice:
                        # logging.debug("Position %s hit its stop loss (tick %s)" % (self, tick))
                        self.exitPrice = tick.bid
                        self.status = Position.PositionStatus.STOP_LOSS

            if self.order.takeProfit is not None:
                if self.order.direction == Direction.LONG and tick.offer >= self.takeProfit:
                    # logging.debug("Position %s hit its take profit target (tick %s)" % (self, tick))
                    self.exitPrice = tick.offer
                    self.status = Position.PositionStatus.TAKE_PROFIT
                elif self.order.direction == Direction.SHORT and tick.bid <= self.takeProfit:
                    # logging.debug("Position %s hit its take profit target (tick %s)" % (self, tick))
                    self.exitPrice = tick.bid
                    self.status = Position.PositionStatus.TAKE_PROFIT

        return self.status

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return "%s: %s [%s %s --> %s]" % (self.id, self.status.name, self.order.direction.name, self.entryPrice, "OPEN" if self.status == Position.PositionStatus.OPEN else self.exitPrice)

    __repr__ = __str__