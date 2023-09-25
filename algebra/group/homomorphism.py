from dataclasses import dataclass, fields, field
from typing import Dict, List

from algebra.group.abstract.base import Group, GroupElement, GroupRep, T
from algebra.group.abstract.permutation import PermutationGroupRep


@dataclass
class GroupDirectProductRep(PermutationGroupRep):
    subgroup_list: List[GroupRep]

    def __hash__(self):
        return hash(f"GDPR{self.degree}")

    def __init__(self, group_rep_list):
        self.subgroup_list = group_rep_list

        object_list = list(self._sub_object_list())
        super().__init__(len(object_list))

        self.object_map_right = dict(zip(object_list, self.object_list()))
        self.object_map_left = dict(zip(self.object_list(), object_list))

    def right_map(self, item: List[GroupElement]):
        if len(item) != len(self.subgroup_list):
            raise ValueError('Dimension not matched')

        for i, g in zip(item, self.subgroup_list):
            if i.group != g:
                raise ValueError('Group not matched')

        mapping = {}
        map_right = self.object_map_right
        for i in item:
            for o1 in i.group.object_list():
                o2 = i.act(o1)
                if o1 != o2:
                    mapping[map_right[o1]] = map_right[o2]

        return self.element(mapping)

    def _sub_object_list(self):
        for subgroup in self.subgroup_list:
            yield from subgroup.object_list()


@dataclass
class GroupHomomorphism:
    domain: Group
    codomain: Group
    mapping: Dict[GroupElement, GroupElement]

    def __post_init__(self):
        # domain의 generator가 모두 맞게 있는지 확인한다.
        domain_gen_set = set(self.domain.generator)
        mapping_set = set(self.mapping)
        if domain_gen_set != mapping_set:
            raise ValueError('Domain Generating Set and Mapping')

        # mapping의 값이 codomain에 포함되어있는지 확인
        for value in self.mapping.values():
            if not self.codomain.element_test(value):
                raise ValueError('Target Value')

        # mapping 값이 제대로 됐는지 확인
        product_order = self.as_direct_product().order()
        if product_order != self.domain.order():
            raise ValueError('Mapping not Hom')

    def image(self):
        return self.codomain.represent.group(
            *self.mapping.values()
        )

    def as_direct_product(self) -> Group:
        # rep 생성
        group_rep = GroupDirectProductRep([
            self.domain.represent,
            self.codomain.represent
        ])

        # generator 생성
        generator = [
            group_rep.right_map(list(items))
            for items in self.mapping.items()
        ]

        return group_rep.group(*generator)

    @staticmethod
    def _scan_group(element: GroupElement, group: Group, object_map):
        for o1 in group.represent.object_list():
            o2 = element.act(o1)
            if o1 != o2:
                yield object_map[o1], object_map[o2]
