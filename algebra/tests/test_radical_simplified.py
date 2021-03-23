import unittest

from algebra.number.util import factorize, is_prime


class TestRadicalMultiply(unittest.TestCase):
    def test_factorization(self):
        for i in range(2, 100):
            with self.subTest(f"Factorize {i}"):
                f = factorize(i)
                for prime, power in f.items():
                    self.assertTrue(is_prime(prime),
                                    "Factor should be a prime")

                i_another = 1
                for prime, power in f.items():
                    i_another *= pow(prime, power)
                self.assertEqual(i, i_another)

        for i in range(7, 30):
            with self.subTest(f"Factorize 2**{3*i}"):
                f = factorize(8 ** i)
                self.assertEqual(len(f), 1)
                self.assertIn(2, f)
                self.assertEqual(f[2], i*3)

        with self.subTest("Figure 1372933"):
            f = factorize(1372933)
            self.assertTrue(is_prime(1372933))
            self.assertEqual(len(f), 1)
            self.assertIn(1372933, f)
            self.assertEqual(f[1372933], 1)
