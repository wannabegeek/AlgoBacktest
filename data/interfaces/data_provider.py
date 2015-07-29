from abc import ABCMeta, abstractmethod

class Provider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def register(self, symbol):
        pass

    @abstractmethod
    def load_historical_data(self, period):
        pass

    @abstractmethod
    def start_publishing(self, callback):
        pass

    def set_progress_callback(self, callback):
        raise NotImplementedError("setProgressCallback isn't implemented for this Provider instance")
