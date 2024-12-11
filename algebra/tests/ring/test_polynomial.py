import unittest

from algebra.field.rational import RationalField
from algebra.ring.polynomial import PolynomialRing, PolynomialIdeal
from algebra.ring.quotient import QuotientRing


class TestPolynomialRing(unittest.TestCase):
    def test_definition(self):
        pr = PolynomialRing(field=RationalField())
        f = pr.element([1, 0, 1])
        f2 = f * f

        self.assertEqual(f2.degree, 4)

    def test_ideal(self):
        pr = PolynomialRing(field=RationalField())
        f = pr.element([1, 0, 1])

        ideal: PolynomialIdeal = pr.ideal([f])

        f1 = pr.element([1, -1, 1, -1])
        self.assertTrue(ideal.is_equivalent(f, f1))

        f2 = pr.element([1, -1, 1, -2])
        self.assertFalse(ideal.is_equivalent(f, f2))

    def test_quotient(self):
        pr = PolynomialRing(field=RationalField())
        f = pr.element([1, 0, 1])
        ideal: PolynomialIdeal = pr.ideal([f])
        modulo: QuotientRing = pr / ideal

        f1 = modulo.element([1, 2, 5, 4, 3])
        f2 = modulo.element([1, 2, 2, 4])
        self.assertTrue(f1 == f2)
