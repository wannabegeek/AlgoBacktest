from enum import Enum
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
                self.stopPrice = tick.bid - self.order.stoploss.points * self.order.symbol.leverage
            else:
                self.stopPrice = tick.offer + self.order.stoploss.points * self.order.symbol.leverage
        else:
            self.stopPrice = None

    def isOpen(self):
        return not self.closed

    def close(self, tick, reason = ExitReason.CLOSED):
        if reason == Position.ExitReason.TAKE_PROFIT:
            self.exitPrice = self.order.takeProfit
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

        return priceDelta * self.order.symbol.leverage

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
                        return Position.ExitReason.STOP_LOSS
                else:
                    if tick.bid >= self.stopPrice:
                        return Position.ExitReason.STOP_LOSS

            if self.order.takeProfit is not None:
                if self.order.direction == Direction.LONG and tick.offer >= self.order.takeProfit:
                    return Position.ExitReason.TAKE_PROFIT
                elif self.order.direction == Direction.SHORT and tick.bid <= self.order.takeProfit:
                    return Position.ExitReason.TAKE_PROFIT
        return Position.ExitReason.NOT_CLOSED

    def __str__(self):
        s = ""
        if self.order.stoploss is not None:
            s = "S/L: {0}{1}".format(self.stopLoss, "[T]" if self.order.stoploss == StopLoss.type.TRAILING else "[F]")
        if self.isOpen():
            result = "{0} {1:3.1f}: {2} --> (Still Open)        ({3:.4f}) {4}".format(self.order.direction.name, self.ratio, self.entryQuote.timestamp,
                                                                        self.entryQuote.close, s)
        else:
            result = "{0} {1:3.1f}: {2} --> {3} ({4:.4f} - {5:.4f} [{6:.4f}]) {7}".format(self.order.direction.name, self.ratio, self.entryQuote.timestamp,
                                                                            self.exitQuote.timestamp,
                                                                            self.entryQuote.close,
                                                                            (self.exitQuote.close if self.adjustedClose is None else self.adjustedClose),
                                                                            self.pointsDelta(),
                                                                            "StopLoss" if self.exitReason == Position.ExitReason.STOP_LOSS
                                                                                else "Take Profit" if self.exitReason == Position.ExitReason.TAKE_PROFIT
                                                                                else "Closed")

        return result
