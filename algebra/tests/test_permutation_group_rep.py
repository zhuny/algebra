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

        print(f"{e1=!s}")
        print(f"{e2=!s}")

        group = perm.group(e1, e2)  # <(0 1 2), (2 3 4)(5 6 7 8)>

        subgroup = group.stabilizer(ol[0])
        for g1 in subgroup.generator:
            print(g1)

    def test_stabilizer_chain_sym(self):
        # Test with symmetric group
        factorial = 2
        for i in range(3, 11):
            perm = PermutationGroupRep(i)
            ol = list(perm.object_list())

            e1 = perm.element(ol)
            e2 = perm.element(ol[:2])

            # symmetric group of order `i`
            group = perm.group(e1, e2)
            factorial *= i
            self.assertEqual(group.stabilizer_chain().order, factorial)

    def test_stabilizer_chain_dihedral(self):
        for i in range(4, 11):
            perm = PermutationGroupRep(i)
            ol = list(perm.object_list())

            e1 = perm.element(ol)
            e2 = perm.element(
                *[
                    (ol[j], ol[-j])
                    for j in range(1, (i + 1) // 2)
                ]
            )
            dihedral = perm.group(e1, e2)
            self.assertEqual(dihedral.stabilizer_chain().order, 2 * i)

    def test_mathieu_group(self):
        with self.subTest("M11"):
            perm = PermutationGroupRep(11)
            ol = list(perm.object_list())

            e1 = perm.element(ol)  # (1,2,3,4,5,6,7,8,9,10,11)
            e2 = perm.element(  # (3,7,11,8)(4,10,5,6)
                (ol[2], ol[6], ol[10], ol[7]),
                (ol[3], ol[9], ol[4], ol[5])
            )
            m11 = perm.group(e1, e2)
            self.assertEqual(m11.order(), 7920)

        with self.subTest("M12"):
            perm = PermutationGroupRep(12)
            ol = list(perm.object_list())

            e1 = perm.element(ol[:-1])  # (0123456789a)
            e2 = perm.element(
                (ol[0], ol[11]), (ol[1], ol[10]), (ol[2], ol[5]),
                (ol[3], ol[7]), (ol[4], ol[8]), (ol[6], ol[9])
            )  # (0b)(1a)(25)(37)(48)(69)
            e3 = perm.element(
                (ol[2], ol[6], ol[10], ol[7]),
                (ol[3], ol[9], ol[4], ol[5])
            )  # (26a7)(3945)
            m12 = perm.group(e1, e2, e3)
            self.assertEqual(m12.order(), 95_040)

        with self.subTest("M24"):
            perm = PermutationGroupRep(24)
            ol = list(perm.object_list())

            e1 = self.from_num(
                perm, ol,
                ((1, 16, 8, 23, 13, 14, 5),
                 (2, 7, 11, 19, 20, 24, 12), (3, 4, 17, 9, 22, 21, 15))
            )
            e2 = self.from_num(
                perm, ol,
                ((1, 24), (2, 21), (3, 10), (4, 22), (5, 9), (6, 23), (7, 8),
                 (11, 18), (12, 20), (13, 14), (15, 19), (16, 17))
            )
            m24 = perm.group(e1, e2)
            self.assertEqual(m24.order(), 244_823_040)

    def test_rubik_cube(self):
        perm = PermutationGroupRep(54)
        ol = list(perm.object_list())

        generator_index = [
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
        ]
        generator = [
            self.from_num(perm, ol, index) for index in generator_index
        ]

        group = perm.group(*generator)

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

    def from_num(self, perm, ol, nums):
        return perm.element(
            *[
                [ol[i - 1] for i in num]
                for num in nums
            ]
        )
