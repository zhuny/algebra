import unittest

from algebra.group.abstract.shortcut import dihedral_group


class TestHomomorphism(unittest.TestCase):
    def test_factor(self):
        g = dihedral_group(10)
        for element in g.element_list():
            # 모두 합쳐서 값이 맞는지 확인
            target = g.represent.identity

            for f in g.factor(element):
                # generator만 나왔는지 확인
                self.assertIn(f, g.generator, 'generator only')
                target += f

            self.assertEqual(target, element, 'factor check')
