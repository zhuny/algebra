import unittest

from algebra.group.abstract.permutation import PermutationGroupRep
from algebra.group.abstract.shortcut import dihedral_group, symmetric_group, \
    quaternion_group, alternative_group


class TestHomomorphism(unittest.TestCase):
    def test_abelian_pair_1(self):
        self._abelian_check([2, 3], [6], True)
        self._abelian_check([2, 3, 7], [42], True)
        self._abelian_check([2, 4, 7], [56], False)
        self._abelian_check([2, 4, 3, 9], [2, 12, 9], True)
        self._abelian_check([2, 4, 3, 9], [8, 27], False)

    def _abelian_check(self, ab1, ab2, result):
        g1 = self._construct_abelian(ab1)
        g2 = self._construct_abelian(ab2)
        self.assertEqual(
            g1.is_isomorphism(g2),
            result,
            f'{g1}, {g2} isomorphism is {result}'
        )

    def _construct_abelian(self, ab):
        g = PermutationGroupRep(degree=sum(ab))
        generator = []

        offset = 0
        for num in ab:
            element_ = [list(range(offset, offset + num))]
            offset += num
            generator.append(element_)

        return g.group(generator, name=str(tuple(ab)).replace(' ', ''))

    def test_abelian_pair_2(self):
        g1 = self._construct_abelian([2, 4])

        pgr = PermutationGroupRep(degree=10)
        g2 = pgr.group([
            [[0, 1]],
            [[2, 3, 4, 5], [6, 7, 8, 9]]
        ])

        self.assertTrue(g1.is_isomorphism(g2))

    def test_abelian_pair_3(self):
        rep = PermutationGroupRep(degree=8)

        g1 = rep.group([
            [[0, 1], [2, 3]],
            [[0, 2], [1, 3]]
        ])
        g2 = rep.group([
            [[4, 5, 6, 7]]
        ])

        self.assertEqual(g1.order(), 4)
        self.assertEqual(g2.order(), 4)
        self.assertTrue(g1.is_abelian())
        self.assertTrue(g2.is_abelian())
        self.assertEqual(g1.get_abelian_key(), [2, 2])
        self.assertEqual(g2.get_abelian_key(), [4])
        self.assertFalse(g1.is_isomorphism(g2))

    def test_abelian_diff_check(self):
        g1 = self._construct_abelian([2, 4])
        g2 = dihedral_group(4)

        self.assertFalse(g1.is_isomorphism(g2))
        self.assertFalse(g2.is_isomorphism(g1))

    def test_non_abelian_pair_1(self):
        g1 = dihedral_group(4)
        g2 = symmetric_group(3)

        # order가 맞지 않음
        self.assertFalse(g1.is_isomorphism(g2))

    def test_non_abelian_pair_2(self):
        g1 = dihedral_group(12)
        g2 = symmetric_group(4)

        # order는 같음
        self.assertFalse(g1.is_isomorphism(g2))

    def test_non_abelian_pair_3(self):
        g1 = quaternion_group()
        g2 = dihedral_group(4)

        # order는 같음
        self.assertFalse(g1.is_isomorphism(g2))

    def test_non_abelian_pair_4(self):
        g1 = alternative_group(4)
        g2 = dihedral_group(6)

        self.assertFalse(g1.is_isomorphism(g2))

    def test_non_abelian_pair_5(self):
        g1 = dihedral_group(6)
        g2 = dihedral_group(6)

        self.assertTrue(g1.is_isomorphism(g2))
