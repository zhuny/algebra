import unittest
from fractions import Fraction

from algebra.polynomial.multi_variable import MultiVariableRing
from algebra.polynomial.polynomial import Polynomial


class TestMultiVariable(unittest.TestCase):
    # 1702.07262v3
    def test_example_2_1(self):
        # example 2.1
        m = MultiVariableRing(2)
        x, y = m.variables()
        i1 = x * x - y
        i2 = y * y - 2 * x + 4
        f = 5 * x - 3 * y

        g = Polynomial([-23, 48, 18, 0, 1])
        gf = g(f)
        gf_mod = gf % i1 % i2
        # As example mentioned, gf_mod should be zero but not check until Grobner bases
        print(gf_mod)

    def test_example_2_5(self):
        m = MultiVariableRing(2)
        x, y = m.variables()
        i1 = x * x - y * y / 7 - 5
        i2 = (y * y * 2 + x * 8 - 7) / 2
        f = 3 * x - 2 * y

        g = Polynomial([Fraction(10967, 28), Fraction(5868, 7), Fraction(-6527, 49), Fraction(24, 7), 1])
        gf = g(f)
        gf_mod = gf % i1 % i2
        # As example mentioned, gf_mod should be zero but not check until Grobner bases
        print(gf_mod)
