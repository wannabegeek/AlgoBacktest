class SymbolRequestType(object):
    CLOSING = 'CLOSING'
    INTRADAY = 'INTRADAY'
    REALTIME = 'REALTIME'

class SymbolRequestPeriod(object):
    MIN_1 = 60
    MIN_5 = 300
    MIN_10 = 600
    MIN_15 = 900
    MIN_30 = 1800
    HOUR_1 = 3600
    HOUR_2 = 7200
    HOUR_4 = 14400
    DAY = 86400
    WEEK = 604800


class BackTestDataProvider(object):
    symbol = None
    period = None

    def __init__(self, symbol, period):
        self.symbol = symbol
        self.period = period

    def request(self, callback):
        raise NotImplementedError
