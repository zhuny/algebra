import itertools
from typing import Dict, List, Type

from pydantic import BaseModel

from algebra.group.abstract.base import Group, GroupElement, GroupRep


class DirectProductGroupRep(GroupRep):
    rep_list: tuple[GroupRep, ...]

    @property
    def group_cls(self) -> Type:
        return DirectProductGroup

    @property
    def cls_element(self) -> Type:
        return DirectProductGroupElement

    def element(self, element):
        if not isinstance(element, (tuple, list)):
            raise ValueError("Tuple or list expected")

        if len(element) != len(self.rep_list):
            raise ValueError("Length not matched")

        return self.cls_element(
            represent=self,
            value_list=tuple(
                rep.element(e)
                for e, rep in zip(element, self.rep_list)
            )
        )

    def as_group(self):
        group_list = [rep.as_group() for rep in self.rep_list]
        gen_list = [g.generator for g in group_list]
        return self.group(elements=list(itertools.product(*gen_list)))


class DirectProductGroupElement(GroupElement):
    represent: DirectProductGroupRep
    value_list: tuple[GroupElement, ...]


class DirectProductGroup(Group):
    represent: DirectProductGroupRep
    generator: tuple[DirectProductGroupElement, ...]


class GroupHomomorphism(BaseModel):
    domain: Group
    codomain: Group
    mapping: Dict[GroupElement, GroupElement]
    raise_exception: bool = True

    def model_post_init(self, __context):
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
        if self.raise_exception:
            if not self.is_valid_structure():
                raise ValueError('Mapping not Hom')

    def is_valid_structure(self):
        product_order = self.as_direct_product().order()
        return product_order == self.domain.order()

    def value(self, element):
        if not self.domain.element_test(element):
            raise ValueError('Not Element of domain')

        value = self.codomain.represent.identity

        mapping = {}
        for g, h in self.mapping.items():
            mapping[g] = h
            mapping[-g] = -h

        for f in self.domain.factor(element):
            value += mapping[f]
        return value

    def value_group(self, group: Group):
        return Group(
            represent=self.codomain.represent,
            generator=[
                self.value(g)
                for g in group.generator
            ]
        )

    def kernel(self) -> 'Group':
        direct = self.as_direct_product()
        stabilizer = direct.stabilizer_many([
            direct.represent.right_object_map(o)
            for o in self.codomain.represent.object_list()
        ])

        generator = []
        for g in stabilizer.generator:
            item = direct.represent.left_element_mep(g)
            generator.append(item[0])

        return self.domain.represent.group(*generator)

    def image(self):
        return self.codomain.represent.group(
            *self.mapping.values()
        )

    def as_direct_product(self) -> Group:
        # rep 생성
        group_rep = GroupDirectProductRep(subgroup_list=[
            self.domain.represent,
            self.codomain.represent
        ])

        # generator 생성
        generator = [
            group_rep.right_element_map(list(items))
            for items in self.mapping.items()
        ]

        return group_rep.group(*generator)

    @staticmethod
    def _scan_group(element: GroupElement, group: Group, object_map):
        for o1 in group.represent.object_list():
            o2 = element.act(o1)
            if o1 != o2:
                yield object_map[o1], object_map[o2]
