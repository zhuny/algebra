import unittest

from algebra.group.abstract.permutation import PermutationGroupRep


class TestGroupCenter(unittest.TestCase):
    def test_symmetric_group(self):
        perm = PermutationGroupRep(8)
        ol = list(perm.object_list())

        group = perm.group(
            perm.element(ol[:4]), perm.element(ol[:2]),
            perm.element(ol[4:]), perm.element(ol[4:6])
        )

        symm_center = group.center()
        self.assertTrue(symm_center.is_trivial())
