from abc import ABCMeta, abstractmethod

class AlgoSignalIndicator(object):
    NoAction = 0
    EnterLong = 1
    EnterShort = 2
    ExitLong = 3
    ExitShort = 4

class AlgoFramework(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.currentContext = None
        pass

    def valid(self):
        return False

    def warmupPeriod(self):
        return 0

    def analysis_symbols(self):
        return self.portfolio_symbols()

    @abstractmethod
    def portfolio_symbols(self):
        pass

    @abstractmethod
    def period(self):
        pass

    def initialiseContext(self, context):
        pass;

    @abstractmethod
    def evaluateTickUpdate(self, context, quote):
        pass
