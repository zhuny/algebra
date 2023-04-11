import unittest

from algebra.group.abstract.shortcut import symmetric_group, alternative_group


class TestShortcut(unittest.TestCase):
    def test_symmetric_correct(self):
        factorial = 1
        for i in range(1, 16):
            factorial *= i

            sym_group = symmetric_group(i)

            self.assertEqual(sym_group.order(), factorial)

    def test_symmetric_error(self):
        with self.assertRaises(ValueError):
            symmetric_group(0)
        with self.assertRaises(ValueError):
            symmetric_group(-1)

        with self.assertRaises(TypeError):
            symmetric_group("5")

    def test_alternative_correct(self):
        factorial = 1
        for i in range(2, 16):
            factorial *= i

            alt_group = alternative_group(i)

            self.assertEqual(alt_group.order(), factorial // 2)

        self.assertEqual(
            alternative_group(1).order(),
            1
        )
