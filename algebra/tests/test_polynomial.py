import unittest

from algebra.polynomial.polynomial import Polynomial


class TestPolynomial(unittest.TestCase):
    def test_add(self):
        p1 = Polynomial({i: i for i in range(100)})
        p2 = Polynomial({i: 100 - i for i in range(100)})
        p3 = p1 + p2
        p4 = Polynomial({i: 100 for i in range(100)})
        self.assertEqual(p3, p4)

    def test_sub(self):
        p1 = Polynomial({i: i * i for i in range(100)})
        p2 = Polynomial({i: i for i in range(100)})
        p3 = p1 - p2
        p4 = Polynomial({i: i * i - i for i in range(100)})
        self.assertEqual(p3, p4)

    def test_mul(self):
        p1 = Polynomial({i: 1 for i in range(100)})
        p2 = p1 * p1
        p3 = Polynomial({i: min(i + 1, 199 - i) for i in range(199)})
        self.assertEqual(p2, p3)

    def test_error(self):
        p = Polynomial()

        with self.subTest("__mul__ type error"):
            with self.assertRaises(ValueError):
                p = p * ()

        with self.subTest("__truediv__ type error"):
            with self.assertRaises(ValueError):
                p = p / ()

    def test_diff(self):
        p = Polynomial({1: 1, 2: 1, 3: 1, 4: 1})
        self.assertEqual(p.diff(), Polynomial({0: 1, 1: 2, 2: 3, 3: 4}))
        print(p.diff().to_wolfram_alpha())
