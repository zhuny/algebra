import unittest

from algebra.group.abstract.permutation import PermutationGroupRep


class TestGroupCenter(unittest.TestCase):
    def test_symmetric_group(self):
        """
        S_n is trivial for n >= 3
        """
        factorial = 2
        for n in range(3, 8):
            factorial *= n

            with self.subTest(f"Center of S_{n} is trivial"):
                perm = PermutationGroupRep(n)
                ol = list(perm.object_list())

                group = perm.group(perm.element(ol), perm.element(ol[:2]))

                self.assertEqual(group.order(), factorial)

                symm_center = group.center()
                self.assertTrue(symm_center.is_trivial())

    def test_abelian_group(self):
        """
        Center of abelian group is itself
        """
        for x in range(2, 5):
            for y in range(2, 5):
                perm = PermutationGroupRep(x + y)
                ol = list(perm.object_list())

                group = perm.group(
                    perm.element(ol[:x]),
                    perm.element(ol[x:])
                )

                # TODO: Check this group is abelian
                self.assertEqual(group.order(), x * y)

                center = group.center()
                self.assertEqual(center.order(), x * y)

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
