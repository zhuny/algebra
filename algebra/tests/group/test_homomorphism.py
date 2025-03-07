import unittest

from algebra.group.abstract.permutation import PermutationGroupRep
from algebra.group.abstract.shortcut import dihedral_group, symmetric_group, \
    cyclic_group, alternative_group
from algebra.group.homomorphism import GroupHomomorphism, DirectProductGroupRep


class TestGroupProductDirect(unittest.TestCase):
    def test_group_order(self):
        gr1 = PermutationGroupRep(degree=4)
        gr2 = PermutationGroupRep(degree=5)

        prod = DirectProductGroupRep(rep_list=(gr1, gr2))

        print(prod.as_group())

        self.assertEqual(
            prod.as_group().order(),
            gr1.as_group().order() * gr2.as_group().order()
        )

        e1 = prod.element([
            [[0, 1], [2, 3]],  # gr1 기준
            [[0, 1, 2, 3, 4]]  # gr2 기준
        ])
        self.assertEqual(e1.order(), 10)


@unittest.skipIf(True, "Homomorphism이 permutation 중심")
class TestHomomorphism(unittest.TestCase):
    def test_factor(self):
        g = dihedral_group(10)

        generator_with_inv = []
        for generator in g.generator:
            generator_with_inv.append(generator)
            generator_with_inv.append(-generator)

        for element in g.element_list():
            # 모두 합쳐서 값이 맞는지 확인
            target = g.represent.identity

            for f in g.factor(element):
                # generator만 나왔는지 확인
                self.assertIn(f, generator_with_inv, 'generator only')
                target += f

            self.assertEqual(target, element, 'factor check')

    @unittest.skip
    def test_factor_symmetric(self):
        g = symmetric_group(10)
        total_count = 30
        total_factor_length = 0

        for _ in range(total_count):
            element = g.random_element()
            factor_list = g.factor(element)
            total_factor_length += len(factor_list)

        print(f'average length : {total_factor_length / total_count}')
        print(g.order())

    def test_trivial_hom(self):
        domain = symmetric_group(8)
        codomain = dihedral_group(4)
        m = {
            g: codomain.represent.identity
            for g in domain.generator
        }
        hom = GroupHomomorphism(domain=domain, codomain=codomain, mapping=m)
        hom_image = hom.image()
        self.assertEqual(hom_image.order(), 1)  # trivial group
        self.assertEqual(hom.kernel().order(), domain.order())

    def test_symmetric_with_al(self):
        # Domain Setting
        n = 8
        domain = alternative_group(n)
        domain.generator.append(
            domain.represent.element([[0, 1]])
        )
        self.assertEqual(domain.order(), 40_320)

        # Codomain Setting
        codomain = cyclic_group(2)
        one = codomain.generator[0]
        zero = codomain.represent.identity

        mapping = {
            g: zero if g.order() == 3 else one
            for g in domain.generator
        }
        hom = GroupHomomorphism(
            domain=domain, codomain=codomain,
            mapping=mapping
        )

        self.assertEqual(hom.image().order(), 2)
        self.assertEqual(hom.kernel().order(), 20_160)
        self.assertTrue(domain.is_normal(hom.kernel()))
