import unittest

from algebra.number.radical import Radical


class TestRadicalMultiply(unittest.TestCase):
    def test_simple_sqrt(self):
        for i in range(2, 100):
            n = Radical.from_number(i)
            n_root = n.sqrt()
            n_root_sqrt = n_root * n_root
            with self.subTest(f"sqrt({i}) ** 2 == {i}"):
                self.assertEqual(n, n_root_sqrt)

    def test_cancel_sqrt(self):
        for i in range(2, 100):
            n = Radical.from_number(i)
            n_root = n.sqrt()
            with self.subTest(f"sqrt({i}) - sqrt({i}) == 0"):
                self.assertEqual(n_root - n_root, 0)

    def test_hard_cancel_sqrt(self):
        # (sqrt(2) + sqrt(3)) ** 2 = 5 + 2 * sqrt(6)
        number1 = Radical.from_number(2).sqrt() + Radical.from_number(3).sqrt()
        number1 = number1 * number1

        number2 = Radical.from_number(6).sqrt() * 2 + 5

        self.assertEqual(number1, number2)

    def test_hash_func(self):
        sqrt_2_2 = Radical.from_number(2).sqrt() * 2
        sqrt_8 = Radical.from_number(8).sqrt()

        self.assertEqual(sqrt_2_2, sqrt_8)

        number_set = set()
        number_set.add(sqrt_2_2)
        number_set.add(sqrt_8)

        self.assertEqual(len(number_set), 1)

    def test_simple_expr(self):
        sqrt6_2 = Radical.from_number(6).sqrt() / 2
        sqrt2 = Radical.from_number(2).sqrt()

        sqrt3 = sqrt2 * sqrt6_2  # 2*sqrt(3)/2) is not allowed

        self.assertEqual(sqrt3.to_wolfram_alpha(), "sqrt{3}")
