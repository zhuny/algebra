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

    def test_dihedral_even(self):
        """
        Center of D_4n is <r^2n>
        """
        for n in range(2, 11):
            perm = PermutationGroupRep(n * 2)
            ol = list(perm.object_list())

            e1 = perm.element(ol)
            e2 = perm.element(
                *[
                    (ol[j], ol[-j])
                    for j in range(1, n)
                ]
            )
            dihedral = perm.group(e1, e2)
            self.assertEqual(dihedral.order(), n * 4)

            center = dihedral.center()
            r = perm.element(ol)
            gen = r
            for i in range(1, n * 2):
                gen += r

            self.assertEqual(center.order(), 2)
            self.assertTrue(center.element_test(gen))
