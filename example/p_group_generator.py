from algebra.group.abstract.polycyclic.base import PolyCyclicGroupRep


def main():
    # C2 X C2
    g = PolyCyclicGroupRep(degree=2, number=2).as_group()

    pcg = g.p_covering_group()
    pcg.show('Normalized')
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

    for i, c in enumerate(cc.by_class):
        print('Class :', i)
        print('Rep :', c[0])
        (pcg / c[0]).show()


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
