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
