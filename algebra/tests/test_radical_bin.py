from unittest import TestCase

from algebra.number.radical import Radical


class TestRadicalMultiply(TestCase):
    def test_create_number(self):
        for i in range(100):
            with self.subTest(f"Create Number {i}"):
                self.assertEqual(Radical.from_number(i), i)
