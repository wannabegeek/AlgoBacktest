import mysql.connector

class SymbolDataSource(object):
    YAHOO = 5
    GOOGLE = 6
    CMC_MARKETS = 7

class Symbol(object):

    _symbolCache = {}
    _dbConnection = mysql.connector.connect(user='root', database='BlackBox')

    @staticmethod
    def get(identifier):
        try:
            # first search our static cache
            return Symbol._symbolCache[identifier]
        except Exception,e:
            # then the database
            symbol = Symbol(identifier)
            Symbol._symbolCache[identifier] = symbol
            return symbol

    def __init__(self, identifier):
        self.identifier = identifier
        self.name = None
        self.lookup = {}
        self.spread = 1.0

        cursor = self._dbConnection.cursor(buffered=True)
        cursor.callproc('SymbolInfo', [self.identifier, ])
        for result in cursor.stored_results():
            results = result.fetchall()
            if len(results) == 0:
                raise LookupError("Symbol: '{0}' Not Found".format(self.identifier))
            for result in results:
                self.spread = result[4]
        cursor.close()

        cursor = self._dbConnection.cursor(buffered=True)
        cursor.callproc('GetSymbol', [self.identifier, ])
        for result in cursor.stored_results():
            results = result.fetchall()
            if len(results) == 0:
                raise LookupError("Symbol: '{0}' Not Found".format(self.identifier))
            for result in results:
                self.name = result[1]
                self.lookup[result[2]] = result[3]
        cursor.close()

    def referenceSymbol(self, dataSource):
        return self.lookup[dataSource]

    def __str__(self):
        str = "Symbol: {0}\nName: {1}\n".format(self.identifier, self.name)
        str += "Spread: {0}\n".format(self.spread)
        for dataSource in self.lookup.keys():
            str += "\t{0}: {1}".format(dataSource, self.lookup[dataSource])
        return str

    def __hash__(self):
        return hash(str(self.identifier))

    def __eq__(self, other):
        return self.identifier == other.identifier
