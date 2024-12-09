import unittest

from algebra.ring.primary import IntegerRing


class TestPrimaryNumber(unittest.TestCase):
    def test_simple(self):
        ir = IntegerRing()

        ideal = ir.ideal([ir.element(17)])
        self.assertTrue(ideal.is_contained(ir.zero()))
