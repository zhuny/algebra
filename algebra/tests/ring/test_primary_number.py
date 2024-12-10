import unittest
from fractions import Fraction

from algebra.field.rational import RationalField
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

    def test_rational(self):
        rf = RationalField()

        n5 = rf.element(5)
        n2 = rf.element(2)

        self.assertTrue(n5 + n2, 7)
        self.assertTrue(n5 * n2, 10)
        self.assertTrue(n5 - n2, 3)
        self.assertTrue(n5 / n2, Fraction(5, 2))