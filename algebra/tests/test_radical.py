import unittest

from algebra.number.radical import Radical, SimpleRadical, SimpleRadicalElement


class TestRadicalMultiply(unittest.TestCase):
    def test_error_input(self):
        with self.assertRaises(ValueError):
            Radical(inv=-1, body=SimpleRadical(constant=0))
        with self.assertRaises(ValueError):
            Radical(inv=0, body=SimpleRadical(constant=0))

    def test_sin_60(self):
        sin_60 = Radical.from_number(3).sqrt() / 2
        cos_60 = Radical.from_number(1) / 2

        sin_120 = sin_60 * cos_60 * 2
        cos_120 = cos_60 * cos_60 - sin_60 * sin_60

        sin_180 = sin_120 * cos_60 + cos_120 * sin_60
        cos_180 = cos_60 * cos_120 - sin_60 * sin_120

        self.assertEqual(sin_60.to_wolfram_alpha(), "(sqrt{3})/2")
        self.assertEqual(sin_180, 0)
        self.assertEqual(cos_180, -1)

    def test_another_index(self):
        number = SimpleRadicalElement(
            multiplier=2,
            index=3,
            radicand=SimpleRadical(constant=3)
        )
        self.assertEqual(number.to_wolfram_alpha(), "2*sqrt[3]{3}")
