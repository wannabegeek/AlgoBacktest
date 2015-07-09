from enum import Enum
import logging
import uuid

from strategycontainer.order import StopLoss, Direction, State, Order
from strategycontainer.price import Tick


class Position(object):
    class ExitReason(Enum):
        NOT_CLOSED = 0
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
        self.exitReason = Position.ExitReason.NOT_CLOSED
        self.exitPrice = None
        if self.order.stoploss is not None:
            if self.order.direction == Direction.LONG:
                self.stopPrice = tick.bid - self.order.stoploss.points / 10**self.order.symbol.leverage
            else:
                self.stopPrice = tick.offer + self.order.stoploss.points / 10**self.order.symbol.leverage
        else:
            self.stopPrice = None

        if self.order.takeProfit is not None:
            if self.order.direction == Direction.LONG:
                self.takeProfit = tick.bid + self.order.takeProfit / 10**self.order.symbol.leverage
            else:
                self.takeProfit = tick.offer - self.order.takeProfit / 10**self.order.symbol.leverage
        else:
            self.takeProfit = None


    def isOpen(self):
        return not self.closed

    def close(self, tick, reason = ExitReason.CLOSED):
        if reason == Position.ExitReason.TAKE_PROFIT:
            self.exitPrice = self.takeProfit
        else:
            if self.order.direction == Direction.LONG:
                self.exitPrice = tick.offer
            else:
                self.exitPrice = tick.bid

        self.exitTick = tick
        self.closed = True
        self.exitReason = reason

    def pointsDelta(self):
        priceDelta = 0.0
        if self.order.direction == Direction.LONG:
            priceDelta = self.exitPrice - self.entryPrice
        else:
            priceDelta = self.entryPrice - self.exitPrice

        return priceDelta * 10**self.order.symbol.leverage

    def shouldClosePosition(self, tick):
        if self.isOpen():
            if self.order.stoploss is not None:
                if self.order.stoploss.type == StopLoss.Type.TRAILING:
                    if self.order.direction == Direction.LONG:
                        self.stopPrice = max(self.stopPrice, tick.bid - self.order.stoploss.points * self.order.symbol.leverage)
                    else:
                        self.stopPrice = min(self.stopPrice, tick.offer + self.order.stoploss.points * self.order.symbol.leverage)

                if self.order.direction == Direction.LONG:
                    if tick.offer <= self.stopPrice:
                        # logging.debug("Position %s hit its stop loss (tick %s)" % (self, tick))
                        self.exitReason = Position.ExitReason.STOP_LOSS
                        self.exitPrice = tick.offer
                else:
                    if tick.bid >= self.stopPrice:
                        # logging.debug("Position %s hit its stop loss (tick %s)" % (self, tick))
                        self.exitPrice = tick.bid
                        self.exitReason = Position.ExitReason.STOP_LOSS

            if self.order.takeProfit is not None:
                if self.order.direction == Direction.LONG and tick.offer >= self.takeProfit:
                    # logging.debug("Position %s hit its take profit target (tick %s)" % (self, tick))
                    self.exitPrice = tick.offer
                    self.exitReason = Position.ExitReason.TAKE_PROFIT
                elif self.order.direction == Direction.SHORT and tick.bid <= self.takeProfit:
                    # logging.debug("Position %s hit its take profit target (tick %s)" % (self, tick))
                    self.exitPrice = tick.bid
                    self.exitReason = Position.ExitReason.TAKE_PROFIT

        return self.exitReason

    def __str__(self):
        return "%s: %s [%s %s --> %s]" % (self.id, self.exitReason.name, self.order.direction.name, self.entryPrice, "OPEN" if self.exitReason == Position.ExitReason.NOT_CLOSED else self.exitPrice)

    __repr__ = __str__