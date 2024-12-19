import math
import unittest

from algebra.field.radical.base import ODRadical


class TestRadicalCeil(unittest.TestCase):
    def test_simple(self):
        root2 = ODRadical.from_number(2)
        self.assertEqual(math.ceil(root2), 1)

        root3 = ODRadical.from_number(3)
        self.assertEqual(math.ceil(root3), 1)

        self.assertEqual(math.ceil(root2 + root3), 3)
        self.assertEqual(math.ceil(root3 - root2), 0)
        self.assertEqual(math.ceil(root2 * root3), 2)

        self.assertEqual(math.ceil(root2 * root2), 2)

        root5 = ODRadical.from_number(5)
        self.assertEqual(math.ceil(root2 + root3 + root5), 5)
        self.assertEqual(math.ceil(root2 / (root3 + root5)), 0)

        inv = root3 / (root2 + root5)
        inv *= root2 + root5
        self.assertEqual(inv, root3)
