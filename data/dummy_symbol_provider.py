import logging
from data.interfaces.symbol_data_provider import SymbolProvider, SymbolProviderData


class DummySymbolProvider(SymbolProvider):

    def getDataForSymbol(self, sid):
        return {SymbolProviderData.identifier: 1, SymbolProviderData.name: "Dummy Symbol", SymbolProviderData.asset_class: 1, SymbolProviderData.lot_size: 10000}

