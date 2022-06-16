import unittest

from algebra.group.abstract.permutation import PermutationGroupRep


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

    def test_orbit(self):
        perm = PermutationGroupRep(5)
        a0, a1, a2, a3, a4 = perm.object_list()
        e1 = perm.element(a0, a1, a2)  # (0 1 2)
        group = perm.group(e1)  # <(0 1 2)>

        self.assertSetEqual(group.orbit(a0), {a0, a1, a2})
        self.assertSetEqual(group.orbit(a1), {a0, a1, a2})
        self.assertSetEqual(group.orbit(a2), {a0, a1, a2})
        self.assertSetEqual(group.orbit(a3), {a3})
        self.assertSetEqual(group.orbit(a4), {a4})

    def test_stabilizer(self):
        perm = PermutationGroupRep(10)

        ol = list(perm.object_list())

        e1 = perm.element(*ol[:3])  # (0 1 2)
        e2 = perm.element(ol[2:5], ol[5:9])  # (2 3 4)(5 6 7 8)
        group = perm.group(e1, e2)  # <(0 1 2), (2 3 4)(5 6 7 8)>

        subgroup = group.stabilizer(ol[0])
        for g1 in subgroup.generator:
            print(g1)

    def test_stabilizer_chain(self):
        perm = PermutationGroupRep(8)
        ol = list(perm.object_list())

        e1 = perm.element(ol)
        e2 = perm.element(ol[:2])

        group = perm.group(e1, e2)

        group.stabilizer_chain().show()
