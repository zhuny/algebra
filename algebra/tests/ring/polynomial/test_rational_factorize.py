import unittest

from algebra.field.rational import RationalField
from algebra.ring.polynomial.base import PolynomialRing


class TestRationalFactorize(unittest.TestCase):
    def test_simple_factorize(self):
        pr = PolynomialRing(field=RationalField(), number=1)

        f = pr.element([3, 2, 1])
        for i in range(1, 5):
            f *= pr.element([i, 1])

        answer = 1

        for p, q in f.factorize():
            self.assertEqual(p.ring, pr)
            self.assertEqual(q, 1)
            if p.degree() == 2:
                self.assertTrue(
                    p == pr.element([3, 2, 1])
                )
            answer *= p

        self.assertTrue(f == answer)

    def test_free_square(self):
        pr = PolynomialRing(field=RationalField(), number=1)

        f5 = pr.element([2, 1]) ** 5

        for p, q in f5.factorize():
            self.assertTrue(p == pr.element([2, 1]))
            self.assertEqual(q, 5)

    def test_monic_check(self):
        pr = PolynomialRing(field=RationalField(), number=1)

        f1 = pr.element([2, 1]) ** 4
        f2 = pr.element([3, 1]) ** 3
        f3 = f1 * f2

        for p, q in f3.factorize():
            if p == pr.element([2, 1]):
                self.assertEqual(q, 4)
            elif p == pr.element([3, 1]):
                self.assertEqual(q, 3)
            else:
                self.assertTrue(0)
