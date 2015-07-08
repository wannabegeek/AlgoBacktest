from abc import ABCMeta, abstractmethod

class Provider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def register(self, symbol):
        pass

    @abstractmethod
    def loadHistoricalData(self, period):
        pass

    @abstractmethod
    def startPublishing(self, callback):
        pass
