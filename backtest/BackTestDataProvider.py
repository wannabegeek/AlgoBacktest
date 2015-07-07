import datetime


class SymbolRequestType(object):
    CLOSING = 'CLOSING'
    INTRADAY = 'INTRADAY'
    REALTIME = 'REALTIME'

class SymbolRequestPeriod(object):
    MIN_1 = datetime.timedelta(mintues=1)
    MIN_5 = datetime.timedelta(mintues=5)
    MIN_10 = datetime.timedelta(mintues=10)
    MIN_15 = datetime.timedelta(mintues=15)
    MIN_30 = datetime.timedelta(mintues=30)
    HOUR_1 = datetime.timedelta(hours=1)
    HOUR_2 = datetime.timedelta(hours=2)
    HOUR_4 = datetime.timedelta(hours=4)
    DAY = datetime.timedelta(days=1)
    WEEK = datetime.timedelta(weeks=1)


class BackTestDataProvider(object):
    symbol = None
    period = None

    def __init__(self, symbol, period):
        self.symbol = symbol
        self.period = period

    def request(self, callback):
        raise NotImplementedError
