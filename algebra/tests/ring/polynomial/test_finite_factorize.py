import unittest

from algebra.field.finite_prime import FinitePrimeField
from algebra.ring.polynomial.base import PolynomialRing


class TestFiniteFactorize(unittest.TestCase):
    def test_power(self):
        pr = PolynomialRing(field=FinitePrimeField(83))

        n = 12
        e1 = pr.element([1, 1])
        e2 = e1 ** n

        t = 1
        for _ in range(n):
            t *= e1

        self.assertTrue(e2 == t)

    def test_simple_factorize(self):
        pr = PolynomialRing(field=FinitePrimeField(83))

        e1 = pr.element([1, 1])
        e2 = pr.element([3, 1])

        f1 = e1 ** 7
        f2 = e2 ** 19

        for f, p in (e1 * e2).factorize():
            if f == f1:
                self.assertEqual(p, 7)
            if f == f2:
                self.assertEqual(p, 19)

    def test_char_validation(self):
        pr = PolynomialRing(field=FinitePrimeField(83))

        e1 = pr.element([1, 2, 3]) ** 83

        for f, p in e1.factorize():
            print(f, p)
            print()
            print()
            print()
            print()
            self.assertEqual(p, 83)
            self.assertTrue((f - e1).is_zero())
