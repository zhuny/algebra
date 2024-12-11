import unittest
from fractions import Fraction

from algebra.field.rational import RationalField
from algebra.ring.polynomial import PolynomialRing, PolynomialIdeal
from algebra.ring.quotient import QuotientRing


class TestPolynomial(unittest.TestCase):
    def test_definition(self):
        pr = PolynomialRing(field=RationalField())
        f = pr.element([1, 0, 1])
        f2 = f * f

        self.assertEqual(f2.lead_monomial().power[0], 4)

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

    def test_minimal_polynomial(self):
        pr = PolynomialRing(field=RationalField(), number=2)
        x, y = pr.variables()

        f1 = x * x - y * y / 7 - 5
        f2 = y * y + 4 * x - Fraction(7, 2)
        ideal = pr.ideal([f1, f2])
        quotient: QuotientRing = pr / ideal

        f = quotient.element(3 * x - 2 * y)
        mp = f.minimal_polynomial()
        self.assertEqual(mp.get(3), Fraction(24, 7))
        self.assertEqual(mp.get(2), Fraction(-6527, 49))
        self.assertEqual(mp.get(1), Fraction(5868, 7))
        self.assertEqual(mp.get(0), Fraction(10967, 28))
