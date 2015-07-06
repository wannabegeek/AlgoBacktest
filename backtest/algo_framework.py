
class AlgoSignalIndicator(object):
    NoAction = 0
    EnterLong = 1
    EnterShort = 2
    ExitLong = 3
    ExitShort = 4

class AlgoFramework(object):
    def __init__(self):
        self.currentContext = None
        pass

    def valid(self):
        return False

    def warmupPeriod(self):
        return 0

    def analysis_symbols(self):
        return self.portfolio_symbols()

    def portfolio_symbols(self):
        raise NotImplementedError("'portfolio_symbols' must be implemented by sub-class")

    def period(self):
        raise NotImplementedError("'period' must be implemented by sub-class")

    def initialiseContext(self, context):
        pass;

    def evaluateTickUpdate(self, context, quote):
        raise NotImplementedError("'evaluateEntry' must be implemented by sub-class")
