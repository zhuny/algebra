import unittest

from algebra.field.rational import RationalField
from algebra.ring.polynomial.base import PolynomialRing


class TestGaloisTheory(unittest.TestCase):
    def test_multi_discriminant(self):
        pr = PolynomialRing(field=RationalField(), number=2)
        x = pr.variable.x[0]
        f = x * x * x + x * x - 2 * x - 1
        self.assertEqual(f.discriminant2(x), 49)

    def test_simple_galois(self):
        self._check_degree_4([1, 0, -10, 0, 1], 4, 'C2 X C2')

    def test_degree_4_ex_24(self):
        self._check_degree_4(
            [3, 1, 2, 0, 1],
            24, 'S4'
        )

    def test_degree_4_ex_40(self):
        self._check_degree_4(
            [1, 1, 1, 1, 1],
            4, 'C4'
        )

    def test_degree_4_ex_41(self):
        self._check_degree_4(
            [1, 0, 0, 0, 1],
            4, 'K4'
        )

    def test_degree_4_ex_43(self):
        self._check_degree_4(
            [12, 8, 0, 0, 1],
            12, 'A4'
        )

    def _check_degree_4(self, element, order, name):
        pr = PolynomialRing(field=RationalField(), number=1)

        f1 = pr.element(element)
        gg1 = f1.galois_group()

        self.assertEqual(gg1.order(), order, f'{name} is expected.')
