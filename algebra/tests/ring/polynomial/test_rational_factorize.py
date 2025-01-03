import unittest

from algebra.field.rational import RationalField
from algebra.ring.polynomial.base import PolynomialRing


class TestRationalFactorize(unittest.TestCase):
    def test_simple_factorize(self):
        pr = PolynomialRing(field=RationalField())

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
