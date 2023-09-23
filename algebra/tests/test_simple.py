import unittest

from algebra.number.simple import Radical


class TestRadicalMultiply(unittest.TestCase):
    def test_simple_sqrt(self):
        # simple mult
        for i in range(2, 11):
            for j in range(2, 20):
                with self.subTest(f"sqrt({i})*sqrt({j})=sqrt({i * j})"):
                    self.assertEqual(
                        Radical.sqrt(i) * Radical.sqrt(j),
                        Radical.sqrt(i * j)
                    )

    def test_sign(self):
        for i in range(2, 11):
            with self.subTest(f"{i} < sqrt({i * i + 1}) < {i + 1}"):
                self.assertTrue((Radical.sqrt(i * i + 1) - i).is_positive())
                self.assertFalse(
                    (Radical.sqrt(i * i + 1) - (i + 1)).is_positive()
                )

    def test_sqrt_ceil(self):
        for i in range(2, 11):
            for j in range(i * i, (i + 1) ** 2):
                with self.subTest(f"ceil(sqrt({j})) = {i}"):
                    self.assertEqual(Radical.sqrt(j).ceil(), i)

    def test_div(self):
        # simple division test
        large = Radical.sqrt(2 * 3 * 5 * 7 * 11 * 13 * 17 * 19)

        for i in range(2, 11):
            for j in range(2, 20):
                lower = Radical.sqrt(i) + Radical.sqrt(j)
                number = large / lower
                self.assertEqual(number * lower, large)

        # divisor stress test
        large = Radical.from_num(1)
        prime_list = [2, 3, 5, 7, 11, 13, 17, 19]
        for prime in prime_list:
            large += Radical.sqrt(prime)

        large_inv = large.inv()
        one = large * large_inv
        self.assertEqual(one, 1)
