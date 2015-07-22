import unittest
from data.dummy_symbol_provider import DummySymbolProvider

from market.symbol import Symbol

class SymbolTest(unittest.TestCase):
    def setUp(self):
        Symbol.setDataProvider(DummySymbolProvider())

    def testSymbol(self):
        s1 = Symbol.get("TEST")
        s2 = Symbol.get("TEST")

        self.assertEqual(s1, s2)
        self.assertEqual(id(s1.__dict__), id(s2.__dict__))
