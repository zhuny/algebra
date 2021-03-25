import unittest

from algebra.number.radical import Radical


class TestRadicalMultiply(unittest.TestCase):
    def test_create_number(self):
        for i in range(100):
            with self.subTest(f"Create Number {i}"):
                self.assertEqual(Radical.from_number(i), i)

    def test_add(self):
        for i in range(1, 100):
            with self.subTest(f"Add Test : (1 + sqrt({i})) ** 2 = "
                              f"{1 + i} + 2 * sqrt({i})"):
                ii = Radical.from_number(i).sqrt()  # sqrt(i)
                ii_1 = ii + 1  # 1 + sqrt(i)
                left_side = ii_1 * ii_1  # (1 + sqrt(i)) ** 2
                right_side = ii * 2 + (i + 1)  # sqrt(i)*2 + i + 1

                self.assertEqual(left_side, right_side)

    def test_mul_nested(self):
        x = (
            Radical.from_number(5).sqrt() +
            Radical.from_number(6).sqrt() * 2
        ).sqrt()
        print(x * x)
