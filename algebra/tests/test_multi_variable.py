import unittest

from algebra.polynomial.multi_variable import MultiVariableRing


class TestPolynomial(unittest.TestCase):
    def test_simple_bin(self):
        m = MultiVariableRing(2)
        x, y = m.variables()
        i1 = x * x - y
        i2 = y * y - 2 * x + 4
        i3 = x + y

        print(i1)
        print(i2)
