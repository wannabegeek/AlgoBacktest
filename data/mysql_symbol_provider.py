import mysql.connector
from data.interfaces.symbol_data_provider import SymbolProvider, SymbolProviderData


class MySQLSymbolProvider(SymbolProvider):

    def __init__(self):
        self._db_connection = mysql.connector.connect(user='blackbox', database='blackbox', host="localhost")
        self.cursor = self._db_connection.cursor(buffered=True)

    def getDataForSymbol(self, sid):
        self.cursor.callproc('symbol_info', [sid, ])
        for results in self.cursor.stored_results():
            for r in results.fetchall():
                return {SymbolProviderData.identifier: r[0], SymbolProviderData.name: r[2], SymbolProviderData.asset_class: r[3], SymbolProviderData.lot_size: r[4]}

        raise LookupError("Symbol: '{0}' Not Found".format(sid))
