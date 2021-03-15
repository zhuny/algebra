import unittest

from algebra.number.radical import Radical


class TestRadicalMultiply(unittest.TestCase):
    def test_simple_sqrt(self):
        for i in range(2, 100):
            n = Radical.from_number(i)
            n_root = n.sqrt()
            n_root_sqrt = n_root*n_root
            with self.subTest(f"sqrt({i}) ** 2 == {i}"):
                self.assertEqual(n, n_root_sqrt)

    def test_cancel_sqrt(self):
        for i in range(2, 100):
            n = Radical.from_number(i)
            n_root = n.sqrt()
            with self.subTest(f"sqrt({i}) - sqrt({i}) == 0"):
                self.assertEqual(n_root-n_root, 0)
