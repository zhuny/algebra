import unittest

from algebra2.group.permutation.simple import SimPermGrpRepresentation


class TestPermutationSimpleCase(unittest.TestCase):
    def test_simple_orbit(self):
        rep = SimPermGrpRepresentation(degree=4)
        group = rep.group([
            [[0, 1, 2, 3]],
            [[1, 3]]
        ], name="D_8")
        self.assertSizeEqual(group.orbit(0), 4)
        self.assertEqual(group.stabilizer(0).order(), 2)
        self.assertEqual(group.order(), 8)

    def assertSizeEqual(self, container, size, msg=None):
        self.assertEqual(len(container), size, msg)
