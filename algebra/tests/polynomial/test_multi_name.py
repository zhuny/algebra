import unittest

from algebra.polynomial.multi_variable import MultiVariableRing


class TestMultiName(unittest.TestCase):
    def test_multi_name(self):
        mv = MultiVariableRing(3)
        x, y, z = mv.variables()

        xxy = x * x * y
        self.assertEqual(str(xxy.lead_monomial()), 'x^2y')

        f = x + y + z
        self.assertEqual(str(f), 'x+y+z')

        f -= 1
        self.assertEqual(str(f), 'x+y+z-1')
