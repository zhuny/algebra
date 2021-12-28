import unittest

from algebra.group.abstract import PermutationGroupRep


class TestPermutationGroupRep(unittest.TestCase):
    def test_add(self):
        perm = PermutationGroupRep(4)
        a0, a1, a2, a3 = perm.object_list()

        e1 = perm.element(a0, a1)  # (0, 1)
        self.assertEqual(e1 + e1, perm.identity)
