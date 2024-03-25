import unittest

from algebra.group.abstract.shortcut import dihedral_group


class TestSylowGroup(unittest.TestCase):
    def test_finest_block_system(self):
        g = dihedral_group(5)
        blocks = g.minimal_block_system()
        self.assertEqual(len(blocks), 5)
