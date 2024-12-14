import unittest
from fractions import Fraction

from algebra.field.finite_prime import FinitePrimeField
from algebra.field.rational import RationalField
from algebra.ring.polynomial.base import PolynomialRing, PolynomialIdeal, \
    PolynomialRingElement
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

    def test_str(self):
        pr = PolynomialRing(field=RationalField(), number=3)
        x, y, z = pr.variables()

        self.assertEqual(str(x), 'x')
        self.assertEqual(str(y), 'y')
        self.assertEqual(str(z), 'z')

        f1 = x * x * y
        self.assertEqual(str(f1), 'x^2y')

        f2 = x + y + z
        self.assertEqual(str(f2), 'x+y+z')

    def test_quotient(self):
        pr = PolynomialRing(field=RationalField())
        f = pr.element([1, 0, 1])
        ideal: PolynomialIdeal = pr.ideal([f])
        modulo: QuotientRing = pr / ideal

        f1 = modulo.element([1, 2, 5, 4, 3])
        f2 = modulo.element([1, 2, 2, 4])
        self.assertTrue(f1 == f2)

    def test_calculate_with_finite_2_1(self):
        pr = PolynomialRing(field=FinitePrimeField(101), number=2)
        x, y = pr.variables()

        f1 = x * x - y
        f2 = y * y - 2 * x - 4

        ideal = pr.ideal([f1, f2])
        quotient: QuotientRing = pr / ideal

        f = quotient.element(5 * x - 3 * y)
        mp: PolynomialRingElement = f.minimal_polynomial()

        expected = mp.ring.element([-23, 48, 18, 0, 1])
        self.assertEqual(mp, expected)

    def test_calculate_with_finite_2_4(self):
        pr = PolynomialRing(field=FinitePrimeField(101), number=2)
        x, y = pr.variables()

        f1 = y * y * y - x * y - 2 * y * y + y
        f2 = x * y * y
        f3 = x * x - x

        ideal = pr.ideal([f1, f2, f3])
        quotient: QuotientRing = pr / ideal

        f = quotient.element(y)
        mp = f.minimal_polynomial()

        # expected = mp.ring.element([0, 0, 1, -2, 1])
        # self.assertEqual(mp, expected)

    def test_minimal_polynomial_2_5(self):
        pr = PolynomialRing(field=RationalField(), number=2)
        x, y = pr.variables()

        f1 = x * x - y * y / 7 - 5
        f2 = y * y + 4 * x - Fraction(7, 2)
        ideal = pr.ideal([f1, f2])
        quotient: QuotientRing = pr / ideal

        f = quotient.element(3 * x - 2 * y)
        mp: PolynomialRingElement = f.minimal_polynomial()

        expected = mp.ring.element([
            Fraction(10967, 28), Fraction(5868, 7),
            Fraction(-6527, 49), Fraction(24, 7),
            1
        ])

        self.assertEqual(mp, expected)

    def test_minimal_polynomial_2_17(self):
        pr = PolynomialRing(field=FinitePrimeField(101), number=6)
        variable_list = list(pr.variables())
        variable_list[4] -= 7
        variable_list[5] -= 1
        ideal = pr.ideal(variable_list)
        quotient: QuotientRing = pr / ideal

        f = 0
        for i, v in enumerate(pr.variables(), 1):
            f += v ** i
        quotient.element(f).minimal_polynomial()
