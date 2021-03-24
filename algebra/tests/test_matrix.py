import unittest

from algebra.matrix.matrix import Matrix


class TestMatrix(unittest.TestCase):
    def _test_fibo(self):
        fibo = Matrix(2, 2)
        fibo[0, 0] = fibo[0, 1] = fibo[1, 0] = 1

        row = Matrix(2, 1)
        row[0, 0] = 1

        fibo1 = fibo
        a, b = 1, 0

        for i in range(100):
            with self.subTest(f"{i}-th fibonacci number"):
                fibo1 *= fibo
                result = fibo1 * row

    def test_boundary_out_error(self):
        m = Matrix(5, 5)
        with self.subTest("Matrix getitem error"):
            with self.subTest("Matrix right"):
                with self.assertRaises(ValueError):
                    print(m[10, 2])
            with self.subTest("Matrix top"):
                with self.assertRaises(ValueError):
                    print(m[2, 10])
            with self.subTest("Matrix bottom"):
                with self.assertRaises(ValueError):
                    print(m[2, -2])
            with self.subTest("Matrix left"):
                with self.assertRaises(ValueError):
                    print(m[2, -2])

        with self.subTest("Matrix setitem error"):
            with self.assertRaises(ValueError):
                m[10, 10] = 1

    def test_matrix_output(self):
        m = Matrix(2, 2)
        m[0, 0] = m[1, 0] = m[0, 1] = 1
        self.assertEqual(m.to_wolfram_alpha(), "{{1,1},{1,0}}")
