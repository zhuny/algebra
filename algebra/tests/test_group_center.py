import unittest

from algebra.group.abstract.permutation import PermutationGroupRep


class TestGroupCenter(unittest.TestCase):
    def test_symmetric_group(self):
        perm = PermutationGroupRep(7)
        ol = list(perm.object_list())

        group = perm.group(perm.element(ol), perm.element(ol[2:]))

        symm_center = group.center()
        self.assertTrue(symm_center.is_trivial())

    def test_abelian_group(self):
        perm = PermutationGroupRep(8)
        ol = list(perm.object_list())

        group = perm.group(
            perm.element(ol[:5]),
            perm.element(ol[5:])
        )
        self.assertEqual(group.order(), 15)

        center = group.center()
        self.assertEqual(center.order(), 15)
