import unittest

from algebra.field.rational import RationalField
from algebra.ring.polynomial.base import PolynomialRing


class TestGaloisTheory(unittest.TestCase):
    def test_simple_galois(self):
        pr = PolynomialRing(field=RationalField(), number=1)

        f = pr.element([1, 0, -10, 0, 1])

        # C2 X C2
        print(f.galois_group())

    def test_degree_4(self):
        pr = PolynomialRing(field=RationalField(), number=1)

        f1 = pr.element([3, 1, 2, 0, 1])

        # S4
        gg1 = f1.galois_group()
        self.assertEqual(gg1.order(), 24)
