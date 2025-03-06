import json

import pydantic
from pydantic import BaseModel

from algebra.group.abstract.permutation import PermutationGroupRep
from algebra.group.abstract.polycyclic.base import PolyCyclicGroupRep, \
    PolyCyclicGroup


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
    # Q8
    g = PolyCyclicGroupRep(
        degree=2, number=3,
        power_relation={0: [2], 1: [2]},
        commute_relation={(1, 0): [2]}
    ).as_group()

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
        print(subgroup)
        for ob in cc.by_class[-1]:
            print('>', ob)
        print(len(cc.element_set))

    reference_group_list = list(get_reference_group_list())
    for reference in reference_group_list:
        print(reference, reference.order(), reference.order_statistics())

    result_relation = RelationContainer()

    for i, c in enumerate(cc.by_class):
        print('Class :', i)
        print('Quotient :', c[0])
        result = pcg / c[0]
        result.represent.show('New :')
        result.show()
        print(result.model_dump())
        for reference in reference_group_list:
            if reference.is_isomorphism(result):
                print('Isomorphic to', reference)  # 2번 이상 출력되면 안됨
        if g.order() == result.order():
            continue
        result_relation.add_relation(g, result)
        print()

    print(result_relation.model_dump())
    # print(json.dumps(result_relation.model_dump(), indent=4))


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


class Relation(BaseModel):
    source: str
    target: str


class RelationContainer(BaseModel):
    group_map: dict[str, PolyCyclicGroup] = pydantic.Field(default_factory=dict)
    relation: list[Relation] = pydantic.Field(default_factory=list)

    def add_relation(self,
                     lower_group: PolyCyclicGroup,
                     upper_group: PolyCyclicGroup):
        key1 = self.add_group(lower_group)
        key2 = self.add_group(upper_group)
        self.relation.append(Relation(source=key1, target=key2))

    def add_group(self, group: PolyCyclicGroup):
        key = group.group_id()
        if key not in self.group_map:
            self.group_map[key] = group
        return key


if __name__ == '__main__':
    main()
