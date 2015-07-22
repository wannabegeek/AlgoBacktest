from abc import ABCMeta, abstractmethod
from enum import Enum


class SymbolProviderData(Enum):
    identifier = 1,
    name = 2,
    asset_class = 3,
    lot_size = 4

class SymbolProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getDataForSymbol(self, sid):
        pass
