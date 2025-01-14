import unittest

from algebra.group.abstract.permutation import PermutationGroupRep


class TestHomomorphism(unittest.TestCase):
    def test_abelian_pair_1(self):
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
        g = PermutationGroupRep(sum(ab))
        generator = []

        offset = 0
        for num in ab:
            element_ = [list(range(offset, offset + num))]
            offset += num
            generator.append(element_)

        return g.group_(generator, name=str(tuple(ab)).replace(' ', ''))
