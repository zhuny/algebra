import unittest

from algebra.field.rational import RationalField
from algebra.ring.polynomial.base import PolynomialRing


class TestPolynomial(unittest.TestCase):
    def test_add(self):
        pr = PolynomialRing(field=RationalField(), number=1)

        p1 = pr.element({i: i for i in range(100)})
        p2 = pr.element({i: 100 - i for i in range(100)})
        p3 = p1 + p2
        p4 = pr.element({i: 100 for i in range(100)})
        self.assertEqual(p3, p4)

    def test_sub(self):
        pr = PolynomialRing(field=RationalField(), number=1)

        p1 = pr.element({i: i * i for i in range(100)})
        p2 = pr.element({i: i for i in range(100)})
        p3 = p1 - p2
        p4 = pr.element({i: i * i - i for i in range(100)})
        self.assertEqual(p3, p4)

    def test_mul(self):
        pr = PolynomialRing(field=RationalField(), number=1)

        p1 = pr.element({i: 1 for i in range(100)})
        p2 = p1 * p1
        p3 = pr.element({i: min(i + 1, 199 - i) for i in range(199)})
        self.assertEqual(p2, p3)

    def test_error(self):
        pr = PolynomialRing(field=RationalField(), number=1)
        p = pr.element({})

        # with self.subTest("__mul__ type error"):
        #     with self.assertRaises(TypeError):
        p = p * ()

        with self.subTest("__truediv__ type error"):
            with self.assertRaises(TypeError):
                p = p / ()

    def test_diff(self):
        pr = PolynomialRing(field=RationalField(), number=1)
        p = pr.element({1: 1, 2: 1, 3: 1, 4: 1})

        self.assertEqual(p.diff(index=0), pr.element({0: 1, 1: 2, 2: 3, 3: 4}))
