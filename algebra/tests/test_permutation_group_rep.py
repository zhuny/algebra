import unittest

from algebra.group.abstract import PermutationGroupRep


class TestPermutationGroupRep(unittest.TestCase):
    def test_add(self):
        perm = PermutationGroupRep(4)
        a0, a1, a2, a3 = perm.object_list()

        e1 = perm.element(a0, a1)  # (0, 1)
        self.assertEqual(e1 + e1, perm.identity)

        e2 = perm.element(a1, a2, a3)  # (1, 2, 3)
        self.assertNotEqual(e2 + e2, perm.identity)
        self.assertEqual(e2 + e2 + e2, perm.identity)
        self.assertEqual(e2 + (-e2), perm.identity)
