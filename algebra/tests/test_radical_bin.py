import unittest

from algebra.number.radical import Radical


class TestRadicalMultiply(unittest.TestCase):
    def test_create_number(self):
        for i in range(100):
            with self.subTest(f"Create Number {i}"):
                self.assertEqual(Radical.from_number(i), i)

    @unittest.skip("For Equal")
    def test_add(self):
        for i in range(1, 100):
            with self.subTest(f"Add Test : (1 + sqrt({i})) ** 2 = "
                              f"{1 + i} + 2 * sqrt({i})"):
                ii = Radical.from_number(i).sqrt()  # sqrt(i)
                ii_1 = ii+1  # 1 + sqrt(i)
                left_side = ii_1 * ii_1  # (1 + sqrt(i)) ** 2
                right_side = ii * 2 + (i + 1)  # sqrt(i)*2 + i + 1
                print(f"i={i}")
                print(f"sqrt(i)={ii}")
                print(f"1+sqrt(i)={ii_1}")
                print(f"(1+sqrt(i))**2={left_side}")
                print(f"sqrt(i)*2+i+1={right_side}")
                self.assertEqual(left_side, right_side)
