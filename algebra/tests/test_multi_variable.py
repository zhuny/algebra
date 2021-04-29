import unittest

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
        gf = g(f) % i1 % i2
        self.assertEqual(gf, 0)
