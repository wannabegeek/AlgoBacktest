from enum import Enum
import uuid

class Position(object):
    class ExitReason(Enum):
        NOT_CLOSED = 0
        SIGNAL = 1
        STOP_LOSS = 2
        TAKE_PROFIT = 3

    def __init__(self, order, quote):
        self.order = order
        self.entryQuote = quote
        self.exitQuote = None
        self.minPrice = self.entryQuote.close
        self.maxPrice = self.entryQuote.close
        self.closed = False
        self.id = uuid.uuid4()
        self.exitReason = Position.ExitReason.NOT_CLOSED
        self.adjustedClose = None

    def isOpen(self):
        return not self.closed

    def update(self, quote):
        self.minPrice = min(quote.low, self.minPrice)
        self.maxPrice = max(quote.high, self.maxPrice)
        if self.stopLoss != -1 and self.stopType == PositionStopType.TRAILING:
            offset = self.entryQuote.close - self.stopLoss
            if self.direction == PositionDirection.LONG:
                self.absoluteStopLossValue = max(self.absoluteStopLossValue, quote.high - offset)
            else:
                self.absoluteStopLossValue = min(self.absoluteStopLossValue, quote.low + offset)

    def close(self, quote, reason = Position.ExitReason.SIGNAL):
        self.exitQuote = quote
        if reason == Position.ExitReason.STOP_LOSS:
            self.adjustedClose = self.absoluteStopLossValue
        if reason == Position.ExitReason.TAKE_PROFIT:
            self.adjustedClose = self.takeProfit
        self.closed = True
        self.exitReason = reason

    def pointsDelta(self):
        multiplier = 1 if self.direction == PositionDirection.LONG else -1
        return ((self.exitQuote.close if self.adjustedClose is None else self.adjustedClose) - self.entryQuote.close) * multiplier * self.ratio * (1 / self.symbol.spread)

    def shouldClosePosition(self, quote):
        if self.isOpen():
            multiplier = 1 if self.direction == PositionDirection.LONG else -1

            if self.stopLoss != -1:
                if self.direction == PositionDirection.LONG:
                    if quote.low <= self.absoluteStopLossValue:
                        return Position.ExitReason.STOP_LOSS
                else:
                    if quote.high >= self.absoluteStopLossValue:
                        return Position.ExitReason.STOP_LOSS

            if self.takeProfit != -1 and (quote.high - self.entryQuote.close) * multiplier * self.ratio >= self.takeProfit:
                return Position.ExitReason.TAKE_PROFIT
        return Position.ExitReason.NOT_CLOSED

    def __str__(self):
        d = "LONG  " if self.direction == PositionDirection.LONG else "SHORT "
        s = ""
        if self.stopLoss != -1:
            s = "S/L: {0}{1}".format(self.stopLoss, "[T]" if self.stopType == PositionStopType.TRAILING else "[F]")
        if self.isOpen():
            result = "{0} {1:3.1f}: {2} --> (Still Open)        ({3:.4f}) {4}".format(d, self.ratio, self.entryQuote.timestamp,
                                                                        self.entryQuote.close, s)
        else:
            result = "{0} {1:3.1f}: {2} --> {3} ({4:.4f} - {5:.4f} [{6:.4f}]) {7}".format(d, self.ratio, self.entryQuote.timestamp,
                                                                            self.exitQuote.timestamp,
                                                                            self.entryQuote.close,
                                                                            (self.exitQuote.close if self.adjustedClose is None else self.adjustedClose),
                                                                            self.pointsDelta(),
                                                                            "StopLoss" if self.exitReason == Position.ExitReason.STOP_LOSS
                                                                                else "Take Profit" if self.exitReason == PositionExitReason.TAKE_PROFIT
                                                                                else "Signal")

        return result
