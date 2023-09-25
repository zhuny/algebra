from dataclasses import dataclass
from typing import Dict, List

from algebra.group.abstract.base import Group, GroupElement, GroupRep, T
from algebra.group.abstract.permutation import PermutationGroupRep


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

    def as_direct_product(self) -> Group:
        # rep 생성
        object_list = []
        object_list.extend(self.domain.represent.object_list())
        object_list.extend(self.codomain.represent.object_list())
        group_rep = PermutationGroupRep(degree=len(object_list))
        object_map = dict(zip(object_list, group_rep.object_list()))

        generator = []

        # mapping 치환하기
        for target, source in self.mapping.items():
            g = {}
            g.update(self._scan_group(target, self.domain, object_map))
            g.update(self._scan_group(source, self.codomain, object_map))
            generator.append(group_rep.element(g))

        return group_rep.group(*generator)

    def _scan_group(self, element: GroupElement, group: Group, object_map):
        for o1 in group.represent.object_list():
            o2 = element.act(o1)
            if o1 != o2:
                yield object_map[o1], object_map[o2]
