from algebra.group.abstract.permutation import PermutationGroupRep
from algebra.group.abstract.polycyclic.base import PolyCyclicGroupRep


def get_reference_group_list():
    rep = PermutationGroupRep(degree=8)

    yield rep.group([[[0, 1]], [[2, 3]], [[4, 5]]], name='Z2Z2Z2')
    yield rep.group([[[0, 1]], [[2, 3, 4, 5]]], name='Z2Z4')
    yield rep.group([[[0, 1, 2, 3, 4, 5, 6, 7]]], name='Z2Z4')
    yield rep.group([[[0, 1, 2, 3]], [[4, 5, 6, 7]]], name='Z4Z4')
    yield rep.group([[[0, 1, 2, 3]], [[1, 3]]], name='D8')
    yield rep.group([
        [[0, 2, 1, 3], [4, 7, 5, 6]],  # i
        [[0, 4, 1, 5], [2, 6, 3, 7]]  # j
    ], name='Q8')


def main():
    # C2 X C2
    g = PolyCyclicGroupRep(degree=2, number=2).as_group()

    pcg = g.p_covering_group()
    pcg.represent.show('Normalized')
    print(pcg.order())

    for group in pcg.lower_exponent_p_central_series():
        print(group)

    ag = pcg.automorphism_group()
    print('Automorphism :', ag)

    for am in ag.generator:
        print('Map :')
        print(am)
        print('Check :')
        for e in pcg.generator:
            print(e, am.act(e))
        print()

    pm = pcg.lower_exponent_p_central()
    cc = ClassifyContainer()
    for subgroup in pm.subgroup_list():
        if cc.is_element(subgroup):
            continue
        cc.update(ag.orbit(subgroup))

    reference_group_list = list(get_reference_group_list())
    for reference in reference_group_list:
        print(reference, reference.order(), reference.order_statistics())

    for i, c in enumerate(cc.by_class):
        print('Class :', i)
        print('Quotient :', c[0])
        result = pcg / c[0]
        result.represent.show('New :')
        result.show()
        for reference in reference_group_list:
            if reference.is_isomorphism(result):
                print('Isomorphic to', reference)  # 2번 이상 출력되면 안됨
        print()


class ClassifyContainer:
    def __init__(self):
        self.by_class = []
        self.element_set = set()

    def update(self, class_list):
        class_list = list(class_list)
        self.by_class.append(class_list)
        self.element_set.update(class_list)

    def is_element(self, other):
        return other in self.element_set


if __name__ == '__main__':
    main()
