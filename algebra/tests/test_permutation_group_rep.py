import unittest

from algebra.group.abstract.permutation import PermutationGroupRep


class TestPermutationGroupRep(unittest.TestCase):
    def test_add(self):
        perm = PermutationGroupRep(degree=4)

        e1 = perm.element([[0, 1]])  # (0, 1)
        self.assertEqual(e1 + e1, perm.identity)

        e2 = perm.element([[0, 1, 2]])  # (1, 2, 3)
        self.assertNotEqual(e2 + e2, perm.identity)
        self.assertEqual(e2 + e2 + e2, perm.identity)
        self.assertEqual(e2 + (-e2), perm.identity)

    def test_orbit(self):
        perm = PermutationGroupRep(degree=5)
        a0, a1, a2, a3, a4 = perm.object_list()
        group = perm.group([[[0, 1, 2]]])

        self.assertSetEqual(group.orbit(a0), {a0, a1, a2})
        self.assertSetEqual(group.orbit(a1), {a0, a1, a2})
        self.assertSetEqual(group.orbit(a2), {a0, a1, a2})
        self.assertSetEqual(group.orbit(a3), {a3})
        self.assertSetEqual(group.orbit(a4), {a4})

    def test_stabilizer(self):
        perm = PermutationGroupRep(degree=10)

        e1 = [[0, 1, 2]]
        e2 = [[2, 3, 4], [5, 6, 7, 8]]

        group = perm.group([e1, e2])  # <(0 1 2), (2 3 4)(5 6 7 8)>

        for o in perm.object_list():
            subgroup = group.stabilizer(o)
            print(subgroup)

    def test_stabilizer_chain_sym(self):
        # Test with symmetric group
        factorial = 2
        for i in range(3, 11):
            perm = PermutationGroupRep(degree=i)

            e1 = [list(range(i))]
            e2 = [[0, 1]]

            # symmetric group of order `i`
            group = perm.group([e1, e2])
            factorial *= i
            self.assertEqual(group.order(), factorial)

    def test_stabilizer_chain_dihedral(self):
        for i in range(4, 11):
            perm = PermutationGroupRep(degree=i)

            e1 = [list(range(i))]
            e2 = [
                [j, (-j) % i]
                for j in range(1, (i + 1) // 2)
            ]
            dihedral = perm.group([e1, e2])
            self.assertEqual(dihedral.stabilizer_chain().order, 2 * i)

    def test_mathieu_group(self):
        with self.subTest("M11"):
            perm = PermutationGroupRep(degree=11)
            m11 = perm.group([
                [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],
                [
                    [2, 6, 10, 7],
                    [3, 9, 4, 5]
                ]
            ])
            self.assertEqual(m11.order(), 7920)

        with self.subTest("M12"):
            perm = PermutationGroupRep(degree=12)
            m12 = perm.group([
                [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],
                [
                    [0, 11], [1, 10], [2, 5],
                    [3, 7], [4, 8], [6, 9]
                ],
                [
                    [2, 6, 10, 7],
                    [3, 9, 4, 5]
                ]
            ])
            self.assertEqual(m12.order(), 95_040)

        with self.subTest("M24"):
            perm = PermutationGroupRep(degree=24)
            m24 = perm.group([
                [
                    [1, 16, 8, 23, 13, 14, 5],
                    [2, 7, 11, 19, 20, 24, 12],
                    [3, 4, 17, 9, 22, 21, 15]
                ],
                [
                    [1, 24], [2, 21], [3, 10], [4, 22],
                    [5, 9], [6, 23], [7, 8], [11, 18],
                    [12, 20], [13, 14], [15, 19], [16, 17]
                ]
            ])
            self.assertEqual(m24.order(), 244_823_040)

    def test_rubik_cube(self):
        perm = PermutationGroupRep(degree=54)

        group = perm.group([
            [
                [0, 2, 8, 6], [1, 5, 7, 3], [18, 45, 29, 38],
                [19, 46, 28, 37], [20, 47, 27, 36]
            ],
            [
                [9, 11, 17, 15], [10, 14, 16, 12], [24, 51, 35, 44],
                [25, 52, 34, 43], [26, 53, 33, 42]
            ],
            [
                [0, 45, 11, 42], [1, 48, 10, 39], [2, 51, 9, 36],
                [18, 20, 26, 24], [19, 23, 25, 21]
            ],
            [
                [6, 47, 17, 44], [7, 50, 16, 41], [8, 53, 15, 38],
                [27, 29, 35, 33], [28, 32, 34, 30]
            ],
            [
                [0, 27, 15, 24], [3, 30, 12, 21], [6, 33, 9, 18],
                [36, 38, 44, 42], [37, 41, 43, 39]
            ],
            [
                [2, 29, 17, 26], [5, 32, 14, 23], [8, 35, 11, 20],
                [45, 47, 53, 51], [46, 50, 52, 48]
            ]
        ])

        # Check order of Rubik's Cube
        self.assertEqual(
            group.order(),
            43_252_003_274_489_856_000
        )

        # Check stabilizer chain optimizing
        for stabilizer in group.stabilizer_chain().travel():
            self.assertTrue(
                stabilizer.point is None or
                len(stabilizer.transversal) > 1
            )

        for i in range(30):
            random_element = group.random_element()
            self.assertTrue(group.element_test(random_element))

    def test_normal_closure_10(self):
        """
        Test normal closure using S_10
        Known fact - The only non-trivial normal subgroup of S_10 is A_10
        So, for given element e,
            if e is in A_10, the normal closure of {e} is A_10.
            if e is not in A_10, the normal closure of {e} is S_10.
        :return:
        """
        # Create S_10
        perm = PermutationGroupRep(degree=10)
        ol = list(perm.object_list())

        sym_group = perm.as_group()

        factorial_10 = 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1

        self.assertEqual(sym_group.order(), factorial_10)

        # This normal closure should be A_10
        e3 = perm.element([[0, 1, 2]])
        normal_closure_e3 = sym_group.normal_closure([e3])
        self.assertTrue(sym_group.is_normal(normal_closure_e3))
        self.assertEqual(normal_closure_e3.order(), factorial_10 // 2)

        # This normal closure should be itself
        e4 = perm.element([[0, 1, 2, 3]])
        normal_closure_e4 = sym_group.normal_closure([e4])
        self.assertTrue(sym_group.is_normal(normal_closure_e4))
        self.assertEqual(normal_closure_e4.order(), factorial_10)

    def test_normal_closure_4(self):
        """
        Test normal closure using S_4
        Known fack - The non-trivial normal subgroup of S_4 are V_4 and A_4

        :return:
        """
        # Create S_4
        perm = PermutationGroupRep(degree=4)
        sym_group = perm.group([
            [[0, 1, 2, 3]],
            [[0, 1]]
        ])

        self.assertEqual(sym_group.order(), 24)

        # This normal closure should be V_4
        e3 = perm.element([[0, 1], [2, 3]])
        normal_closure_e3 = sym_group.normal_closure([e3])
        self.assertTrue(sym_group.is_normal(normal_closure_e3))
        self.assertEqual(normal_closure_e3.order(), 4)

        # This normal closure should be A_4
        e4 = perm.element([[0, 1, 2]])
        normal_closure_e4 = sym_group.normal_closure([e4])
        self.assertTrue(sym_group.is_normal(normal_closure_e4))
        self.assertEqual(normal_closure_e4.order(), 12)

        # This normal closure should be itself
        e5 = perm.element([[0, 1, 2, 3]])
        normal_closure_e5 = sym_group.normal_closure([e5])
        self.assertTrue(sym_group.is_normal(normal_closure_e5))
        self.assertEqual(normal_closure_e5.order(), 24)

    def test_element_test(self):
        perm = PermutationGroupRep(degree=8)
        ol = list(perm.object_list())

        group = perm.group([
            [[0, 1, 2, 3]], [[0, 1]],
            [[4, 5, 6, 7]], [[4, 5]]
        ])

        self.assertEqual(group.order(), 24 * 24)

        # 그룹 원소가 아닌 값 넣어보기
        with self.assertRaises(ValueError):
            group.normal_closure([
                perm.element(ol[3:5])
            ])
