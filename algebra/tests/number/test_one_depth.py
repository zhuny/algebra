import math
import unittest

from algebra.field.radical.base import ODRadical


class TestRadicalMultiply(unittest.TestCase):
    def test_add(self):
        a1 = ODRadical.from_number(2, root=3)
        a2 = ODRadical.from_number(3, root=4)
        r = a1 + a2
        min_poly = r.minimum_polynomial()
        print(min_poly.to_wolfram_alpha())

        self.assertEqual(min_poly.degree, 12)
        self.assertTrue(min_poly(r).is_zero())

    def test_another(self):
        a1 = ODRadical.from_number(2, root=3)
        a2 = ODRadical.from_number(2, root=5)
        r = a1 + a2
        min_poly = r.minimum_polynomial()
        print(min_poly.to_wolfram_alpha())

        self.assertEqual(min_poly.degree, 15)
        self.assertTrue(min_poly(r).is_zero())

    def test_sqrt_radical(self):
        a1 = ODRadical.from_number(8, root=2)
        r = a1 * a1

        print(a1)

        self.assertTrue(2 in a1.body[0].power)
        self.assertTrue(r == 8)

    @unittest.skip
    def test_ceil_radical(self):
        a1 = ODRadical.from_number(2, root=3)
        a2 = ODRadical.from_number(3, root=4)
        r = a1 + a2

        print(math.ceil(r))
