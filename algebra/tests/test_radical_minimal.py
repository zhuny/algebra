import unittest

from algebra.number.radical import Radical


@unittest.skip
class TestRadicalMultiply(unittest.TestCase):
    @staticmethod
    def sqrt(n):
        return Radical.from_number(n).sqrt()

    def test_minimal_easy(self):
        self.check_minimal_polynomial(
            self.sqrt(2) + self.sqrt(3)
        )
        self.check_minimal_polynomial(
            self.sqrt(2) + self.sqrt(3) * 2
        )
        self.check_minimal_polynomial(
            self.sqrt(2) + self.sqrt(3) + self.sqrt(5)
        )

    def check_minimal_polynomial(self, number):
        p = number.minimal_polynomial()
        print(f"Minimal polynomial of '{number.to_wolfram_alpha()}' is")
        print(f"--> {p.to_wolfram_alpha()}")
