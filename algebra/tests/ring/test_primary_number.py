import unittest

from algebra.ring.primary import IntegerRing


class TestPrimaryNumber(unittest.TestCase):
    def test_simple(self):
        ir = IntegerRing()

        ideal = ir.ideal([ir.element(17)])
        self.assertTrue(ideal.is_contained(ir.zero()))

    def test_quotient_ideal(self):
        ir = IntegerRing()

        ideal = ir.ideal([ir.element(17)])
        quotient = ir / ideal

        n13_ = quotient.element(13)
        n30_ = quotient.element(30)
        self.assertTrue(n13_ == n30_)
