import unittest

from algebra.group.abstract.shortcut import dihedral_group


class TestBlockSystem(unittest.TestCase):
    def test_cube(self):
        g = dihedral_group(5)
        blocks = g.finest_block_system()
        self.assertEqual(len(blocks), 5)
