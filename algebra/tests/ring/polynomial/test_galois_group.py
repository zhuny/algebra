import unittest

from algebra.field.rational import RationalField
from algebra.ring.polynomial.base import PolynomialRing


class TestGaloisTheory(unittest.TestCase):
    def test_simple_factorize(self):
        pr = PolynomialRing(field=RationalField())

        f = pr.element([1, 0, -10, 0, 1])

        print(f.galois_group())
