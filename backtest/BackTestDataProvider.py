import datetime

class SymbolRequestType(object):
    CLOSING = 'CLOSING'
    INTRADAY = 'INTRADAY'
    REALTIME = 'REALTIME'



class BackTestDataProvider(object):
    symbol = None
    period = None

    def __init__(self, symbol, period):
        self.symbol = symbol
        self.period = period

    def request(self, callback):
        raise NotImplementedError
