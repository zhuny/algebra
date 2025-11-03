import unittest

from algebra2.group.permutation.simple import SimPermGrpRepresentation


class TestPermutationSimpleCase(unittest.TestCase):
    def test_simple_orbit(self):
        rep = SimPermGrpRepresentation(degree=4)
        group = rep.group([
            [[0, 1, 2, 3]],
            [[1, 3]]
        ])
        print(group)
        print(group.orbit(0))
