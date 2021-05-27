import unittest
from fractions import Fraction

from algebra.calc.grobner_basis import Ideal
from algebra.polynomial.multi_variable import MultiVariableRing, \
    MultiVariableElement
from algebra.polynomial.polynomial import Polynomial


class TestMultiVariable(unittest.TestCase):
    # 1702.07262v3
    def test_example_2_1(self):
        # example 2.1
        m = MultiVariableRing(2)
        x, y = m.variables()
        i1 = x * x - y
        i2 = y * y - 2 * x + 4
        f = 5 * x - 3 * y

        g = Polynomial([-23, 48, 18, 0, 1])
        gf = g(f)
        gf_mod = gf % i1 % i2
        # As example mentioned,
        # gf_mod should be zero but not check until Grobner bases
        print(gf_mod)

    def test_example_2_5(self):
        m = MultiVariableRing(2)
        x, y = m.variables()
        i1 = x * x - y * y / 7 - 5
        i2 = (y * y * 2 + x * 8 - 7) / 2
        f = 3 * x - 2 * y

        g = Polynomial([Fraction(10967, 28), Fraction(5868, 7),
                       Fraction(-6527, 49), Fraction(24, 7), 1])
        gf = g(f)
        gf_mod = gf % i1 % i2
        # As example mentioned,
        # gf_mod should be zero but not check until Grobner bases
        print(gf_mod)

    def test_simple_number_div_test(self):
        m = MultiVariableRing(2)
        x, y = m.variables()
        i1 = x * x - 2  # x = sqrt(2)
        i2 = y * y - 3  # y = sqrt(3)
        f = x + y  # f = sqrt(2) + sqrt(3)
        print(f)

        # f**2 = 5 + 2*sqrt(6) = 5 + 2xy
        f2: MultiVariableElement = (f * f) % i1 % i2
        self.assertEqual(f2.lead_coefficient(), 2)
        self.assertEqual(f2.lead_monomial(), (x * y).lead_monomial())
        print(f2)

        f3: MultiVariableElement = (
            f2 * f2 - 10 * f2 + 1) % i1 % i2  # f**4 - 10*f**2 + 1 = 0
        print(f3)
        self.assertEqual(f3, MultiVariableElement(m))

    def _sim_frac_sqrt2(self):
        sqrt2 = Fraction(2)
        for i in range(8):
            sqrt2 = (sqrt2 * sqrt2 + 2) / (sqrt2 * 2)
        return sqrt2

    def test_simple_number_div_test2(self):
        m = MultiVariableRing(3)
        x, y, z = m.variables()

        i3 = z * z - 3  # z = sqrt(3)
        i2 = y * y - 6  # y = sqrt(6)
        i1 = x * x - y * 2 - 5  # x = sqrt(2*sqrt(6)+5)

        ideal = Ideal()
        ideal.add(m.constant(1), Polynomial([1]))

        f: MultiVariableElement = x - z  # f = sqrt(2*sqrt(6)+5) - sqrt(3) = sqrt(2)
        px = Polynomial([0, 1])

        pair = ideal.add(f, px)
        for i in range(100):
            element = (pair.element * f) % i1 % i2 % i3
            right = pair.right * px

            pair = ideal.add(element, right)
            print(pair)
            if pair.element == 0:
                break

        right: Polynomial = pair.right
        right = right.to_integer_coefficient()
        print("Multiple of Minimal polynomial of f is", right)
        right_factors = right.factorize()
        print("Factor :", right_factors)

        expected_result = self._sim_frac_sqrt2()

        def zero_distance(func):
            return abs(func(expected_result))

        minimal_polynomial = min(right_factors, key=zero_distance)
        print(
            "Minimal polynomial of sqrt(2*sqrt(6)+5)-sqrt(3) is",
            minimal_polynomial.to_wolfram_alpha()
        )
