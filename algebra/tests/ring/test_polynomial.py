import unittest
from fractions import Fraction

from algebra.field.rational import RationalField
from algebra.polynomial.polynomial import PolynomialRing
from algebra.ring.primary import IntegerRing


class TestPolynomial(unittest.TestCase):
    def test_simple(self):
        pr = PolynomialRing()
        f = pr.element([1, 2])
        f2 = f * f
        print(f2)
        print("HI")
