import collections
import math
import unittest

from algebra.group.abstract.shortcut import (
    symmetric_group, alternative_group, dihedral_group, quaternion_group
)


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

    def test_dihedral_group_correct(self):
        for i in range(3, 25):
            d_n = dihedral_group(i)

            self.assertEqual(d_n.order(), i * 2)

            # get element list and calculate order
            order_count = collections.defaultdict(int)
            for e in d_n.element_list():
                order_count[e.order()] += 1

            # solution - we know the structure
            known_order_count = collections.defaultdict(int)
            known_order_count[1] += 1
            known_order_count[2] += i

            for o in range(1, i):
                known_order_count[i // math.gcd(o, i)] += 1

            self.assertEqual(order_count, known_order_count)

    def test_quaternion_group_correct(self):
        """
        Quaternion 인지 확인
        """
        q8 = quaternion_group()
        self.assertEqual(q8.order(), 8)
        self.assertFalse(q8.is_abelian())

        order_4_list = [
            e
            for e in q8.element_list()
            if e.order() == 4
        ]
        self.assertEqual(len(order_4_list), 6)
