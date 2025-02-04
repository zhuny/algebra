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

    pm = pcg.lower_exponent_p_central()
    for subgroup in pm.subgroup_list():
        print(subgroup)
        for o in ag.orbit(subgroup):
            print('>', o)


class ClassifyContainer:
    def __init__(self):
        self.by_class = []
        self.element_list = []

    def update(self, class_list):
        class_list = list(class_list)
        self.by_class.append(class_list)
        self.element_list.extend(class_list)

    def is_element(self, other):
        for element in self.element_list:
            if element == other:
                return True
        return False


if __name__ == '__main__':
    main()
