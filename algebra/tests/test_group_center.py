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
                perm = PermutationGroupRep(degree=n)
                group = perm.as_group()

                self.assertEqual(group.order(), factorial)

                symm_center = group.center()
                self.assertTrue(group.is_normal(symm_center))
                self.assertTrue(symm_center.is_trivial())

    def test_abelian_group(self):
        """
        Center of abelian group is itself
        """
        for x in range(2, 5):
            for y in range(2, 5):
                perm = PermutationGroupRep(degree=x + y)
                group = perm.group([
                    [range(x)], [range(x, x + y)]
                ])

                self.assertTrue(group.is_abelian())

                # TODO: Check this group is abelian
                self.assertEqual(group.order(), x * y)

                center = group.center()
                self.assertTrue(group.is_normal(center))
                self.assertEqual(center.order(), x * y)

    def test_dihedral_even(self):
        """
        Center of D_4n is <r^2n>
        """
        for n in range(2, 11):
            perm = PermutationGroupRep(degree=n * 2)
            dihedral = perm.group([
                [list(range(perm.degree))],
                [
                    [j, perm.degree - j]
                    for j in range(1, n)
                ]
            ])
            self.assertEqual(dihedral.order(), n * 4)

            center = dihedral.center()
            r = perm.element([list(range(perm.degree))])
            r *= perm.degree

            self.assertTrue(dihedral.is_normal(center))
            self.assertEqual(center.order(), 2)
            self.assertTrue(center.element_test(r))

    def test_normal_check(self):
        perm = PermutationGroupRep(degree=4)
        symmetric = perm.as_group()

        # V4 is normal subgroup of S4
        g1 = perm.group([
            [[0, 1], [2, 3]],
            [[0, 2], [1, 3]]
        ])
        self.assertTrue(symmetric.is_normal(g1))

        g2 = perm.group([
            [[0, 1], [2, 3]]
        ])
        self.assertFalse(symmetric.is_normal(g2))

        g3 = perm.group([[[0, 1, 2, 3]]])
        self.assertFalse(symmetric.is_normal(g3))
