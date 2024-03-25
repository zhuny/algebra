import unittest

from algebra.group.abstract.base import Group
from algebra.group.abstract.permutation import PermutationGroupRep
from algebra.group.abstract.shortcut import dihedral_group, symmetric_group
from algebra.number.util import prime_list


class TestSylowGroup(unittest.TestCase):
    def test_finest_block_system(self):
        g = dihedral_group(5)
        blocks = g.minimal_block_system()
        self.assertEqual(len(blocks), 5)

    def _get_product_7_3(self):
        rep = PermutationGroupRep(10)

        return rep.group_([
            [[0, 1]],
            [[0, 1, 2, 3, 4, 5, 6]],
            [[7, 8]],
            [[7, 8, 9]]
        ])

    def _group_list(self):
        yield 'D(4)', dihedral_group(4)
        yield 'D(5)', dihedral_group(5)
        yield 'S(7) X S(3)', self._get_product_7_3()

    def _iter_by_group(self, group):
        order = group.order()
        count = 2

        # 가장 큰 prime divisor보다 2번째 더 큰 prime까지
        for p in prime_list():
            yield p

            if order == 1:
                count -= 1
                if count == 0:
                    break
            while order % p == 0:
                order //= p

    def test_sylow_p_group(self):
        for name, group in self._group_list():
            for prime in self._iter_by_group(group):
                with self.subTest(f'{prime}-Sylow group of {name}'):
                    self._check_sylow(group, prime)

    def _check_sylow(self, group: Group, prime: int):
        sylow_group = group.sylow_group(prime)

        order = group.order()
        sylow_order = 1
        while order % prime == 0:
            order //= prime
            sylow_order *= prime

        self.assertEqual(sylow_group.order(), sylow_order)
