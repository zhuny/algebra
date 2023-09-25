import unittest

from algebra.group.abstract.shortcut import dihedral_group, symmetric_group
from algebra.group.homomorphism import GroupHomomorphism


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

    def test_trivial_hom(self):
        domain = symmetric_group(8)
        codomain = dihedral_group(4)
        m = {
            g: codomain.represent.identity
            for g in domain.generator
        }
        hom = GroupHomomorphism(domain, codomain, m)
        hom_image = hom.image()
        self.assertEqual(hom_image.order(), 1)  # trivial group
