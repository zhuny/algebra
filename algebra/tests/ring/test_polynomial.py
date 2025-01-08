import unittest
from fractions import Fraction

from algebra.field.finite_prime import FinitePrimeField
from algebra.field.rational import RationalField
from algebra.ring.polynomial.base import PolynomialRing, PolynomialIdeal, \
    PolynomialRingElement
from algebra.ring.polynomial.monomial_ordering import MonomialOrderingBase, \
    LexicographicMonomialOrdering, GradedLexicographicOrdering, \
    GradedReverseLexicographicOrdering
from algebra.ring.polynomial.variable import VariableSystem
from algebra.ring.quotient import QuotientRing


class TestPolynomial(unittest.TestCase):
    def test_definition(self):
        pr = PolynomialRing(field=RationalField(), number=1)
        f = pr.element([1, 0, 1])
        f2 = f * f

        self.assertEqual(f2.lead_monomial().power[0], 4)

    def test_ideal(self):
        pr = PolynomialRing(field=RationalField(), number=1)
        f = pr.element([1, 0, 1])

        ideal: PolynomialIdeal = pr.ideal([f])

        f1 = pr.element([1, -1, 1, -1])
        self.assertTrue(ideal.is_equivalent(f, f1))

        f2 = pr.element([1, -1, 1, -2])
        self.assertFalse(ideal.is_equivalent(f, f2))

    def test_str(self):
        pr = PolynomialRing(
            field=RationalField(),
            variable_system=VariableSystem(naming='xyz'))
        x, y, z = pr.variables()

        self.assertEqual(str(x), 'x')
        self.assertEqual(str(y), 'y')
        self.assertEqual(str(z), 'z')

        f1 = x * x * y
        self.assertEqual(str(f1), 'x^2y')

        f2 = x + y + z
        self.assertEqual(str(f2), 'x+y+z')

    def test_quotient(self):
        pr = PolynomialRing(field=RationalField(), number=1)
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

    def test_minimal_polynomial_2_2(self):
        pr = PolynomialRing(field=FinitePrimeField(23), number=3)
        x, y, z = pr.variables()

        g1 = self._poly(x,
                        [1, 8, -6, -8, 4, -4, 5,
                         8, 5, -4, 5, 2, -7, 4, 10, 3, 8])
        g2 = self._poly(y,
                        [1, 9, -9, 7, -8, -4, 9, 1, -5, 7, 1, 10])
        g3 = self._poly(z, [1, -7, 2, 11, -1, 5])
        quotient = pr / pr.ideal([g1, g2, g3])
        f = quotient.element(z).minimal_polynomial()
        self.assertEqual(sum(f.lead_monomial().power), 880)

    def _poly(self, v, coe_list):
        result = 0
        for c in coe_list:
            result = result * v + c
        return result

    def test_monomial_ordering(self):
        with self.subTest("LCO (<> GLCO)"):
            self._test_one_monomial_ordering(
                LexicographicMonomialOrdering(),
                2, True,
                ["x^2", "xy", "x", "y^2", "y", ""]
            )
        with self.subTest("GLCO (<> LCO)"):
            self._test_one_monomial_ordering(
                GradedLexicographicOrdering(),
                2, True,
                ["x^2", "xy", "y^2", "x", "y", ""]
            )
        with self.subTest("GLCO (<>GRLCO)"):
            self._test_one_monomial_ordering(
                GradedLexicographicOrdering(),
                3, False,
                ["x^2", "xy", "xz", "y^2", "yz", "z^2"]
            )
        with self.subTest("GRLCO (<>GLCO)"):
            self._test_one_monomial_ordering(
                GradedReverseLexicographicOrdering(),
                3, False,
                ["x^2", "xy", "y^2", "xz", "yz", "z^2"]
            )

    def _test_one_monomial_ordering(self,
                                    ordering: MonomialOrderingBase,
                                    number: int, constant: bool,
                                    answer: list[str]):
        variables = 'xyz'
        pr = PolynomialRing(
            field=RationalField(),
            variable_system=VariableSystem(
                naming=variables[:number], ordering=ordering
            )
        )
        f = pr.one() if constant else pr.zero()
        f = sum(pr.variables(), start=f)
        f = f * f

        ordered_monomial = list(f.sorted_monomial())

        self.assertEqual(len(ordered_monomial), len(answer))

        for result, expected in zip(ordered_monomial, answer):
            self.assertEqual(str(result), expected)

    def test_grobner_base_small(self):
        pr = PolynomialRing(
            field=RationalField(),
            number=2, variable_system=GradedReverseLexicographicOrdering()
        )
        x, y = pr.variables()

        g1 = x * x + y * y - 1
        g2 = x * y - 2
        quotient = pr / pr.ideal([g1, g2])
        quotient.element(2 * x ** 3 - x * x * y + y ** 3 + 3 * y)

    def test_grobner_base_medium(self):
        pr = PolynomialRing(
            field=RationalField(),
            number=3, variable_system=GradedReverseLexicographicOrdering()
        )
        x, y, z = pr.variables()

        g1 = (x - y) ** 3 - z * z
        g2 = (z - x) ** 3 - y * y
        g3 = (y - z) ** 3 - x * x
        ideal = pr.ideal([g1, g2, g3])
        check = (x ** 10) % ideal

    def test_radical_number(self):
        pr = PolynomialRing(
            field=RationalField(),
            number=3, variable_system=GradedReverseLexicographicOrdering()
        )
        x, y, z = pr.variables()

        g1 = x * x - 2  # sqrt(2)
        g2 = y * y - 8  # sqrt(8)
        g3 = z - x + y  # sqrt(8) - sqrt(2) = sqrt(2)
        ideal = pr.ideal([g1, g2, g3])

        # zeros : +-3sqrt(2), +-sqrt(2)
        quotient = pr / ideal
        mp = quotient.element(z).minimal_polynomial()
        expected = mp.ring.element([36, 0, -20, 0, 1])
        self.assertEqual(mp, expected)

    def test_discriminant(self):
        pr = PolynomialRing(field=RationalField(), number=1)

        f1 = pr.element([-1, -2, 1, 1])
        self.assertEqual(f1.discriminant(0), 49)

        f2 = pr.element({0: -2, 3: 1})
        self.assertEqual(f2.discriminant(0), -108)

        if True:
            return

        # massive calculation
        f3 = pr.element({99: 1, 11: 1, 0: 12})
        self.assertEqual(
            f3.discriminant(0),
            int(
                "-"
                "21264069267243975862417203340924668454099822266732272084763933"
                "01113983760862780495436167041177432088009762326184456604277361"
                "35775289062317200523319479344839407497337627483275712151243145"
                "18630717371581165931390682995091462788698494666134983897512064"
                "83465368487830606817364911723485452912977510400000000000"
            )
        )
