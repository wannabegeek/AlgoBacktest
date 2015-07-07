import unittest

from strategycontainer.symbol import Symbol

class SymbolTest(unittest.TestCase):
    def setUp(self):
        Symbol.setDataProvider("1")

    def testSymbol(self):
        s1 = Symbol("TEST")
        s2 = Symbol("TEST")

        self.assertEqual(s1, s2)
        self.assertEqual(id(s1.__dict__), id(s2.__dict__))
