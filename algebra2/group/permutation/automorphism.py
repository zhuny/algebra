from typing import TypeVar, Type

from algebra2.group.base import GroupDefinition, GroupRepresentation, GroupElement
from algebra2.group.permutation.base import PermutationGroupDefinition, PermutationGroupElement
from algebra2.group.permutation.simple import SimPermGrpRepresentation, SimPermGrpDefinition

# 앞으로 나올 4개를 서로 묶을 타입 변수
R = TypeVar("R", bound="GroupRepresentation")  # representation 타입
E = TypeVar("E", bound="GroupElement")         # element 타입
G = TypeVar("G", bound="GroupDefinition")      # group 타입


class AutoGroupRepresentation(GroupRepresentation[R, E, G]):
    target: GroupDefinition

    def group_cls(self) -> Type[G]:
        return AutoGroupDefinition

    def element(self, auto_map, **kwargs) -> E:
        if isinstance(auto_map, dict):
            auto_map = list(auto_map.items())

        return AutoGroupElement(representation=self, element_map=auto_map)


class AutoGroupElement(GroupElement[R, E, G]):
    element_map: list[tuple[GroupElement, GroupElement]]


class AutoGroupDefinition(GroupDefinition[R, E, G]):
    calc_order: int

    def order(self) -> int:
        return self.calc_order


class AutomorphismBuilder:
    def __init__(self, group: PermutationGroupDefinition):
        self.group = group

        self.right_regular: SimPermGrpDefinition | None = None
        self.rr_element_list: list[PermutationGroupElement] = []
        self.rr_element_index: dict[PermutationGroupElement, int] = {}

        self.holomorph: SimPermGrpDefinition | None = None
        self.auto_generator_list: list[PermutationGroupElement] = []

        self.automorphism: AutoGroupRepresentation | None = None

    def run_right_regular(self):
        group = self.group

        self.rr_element_list = element_list = list(group.iter_elements())

        for index, element in enumerate(element_list):
            self.rr_element_index[element] = index
        element_index = self.rr_element_index

        right_element_list = []
        for e1 in element_list:
            right_element = {}
            for e2 in element_list:
                e3 = e2 * e1
                right_element[element_index[e2]] = element_index[e3]
            right_element_list.append(right_element)

        rep = SimPermGrpRepresentation(degree=len(element_list))
        self.right_regular = rep.group(right_element_list)

    def run_holomorph(self):
        degree = self.right_regular.representation.degree()
        element_list = [[[0, 1]]]
        if degree >= 3:
            element_list.append([list(range(0, degree))])
        sym = self.right_regular.representation.group(element_list)
        self.holomorph, self.auto_generator_list = sym.normalizer_with_quotient(self.right_regular)

    def run_build_auto(self):
        element_list = []
        identity_index = self.rr_element_index[self.group.representation.identity()]
        identity_obj = self.right_regular.representation.object(identity_index)
        stabilizer = self.right_regular.stabilizer(identity_index)
        for generator in self.auto_generator_list:
            acted = generator.act(identity_obj)
            if acted != identity_obj:
                generator = generator / stabilizer.top_layer.transversal[acted]
            element_list.append([
                (self.rr_element_list[k.number], self.rr_element_list[v.number])
                for k, v in generator.data.items()
            ])

        auto_rep = AutoGroupRepresentation(target=self.group)
        self.automorphism = auto_rep.group(
            element_list,
            calc_order=self.holomorph.order() // self.group.order()
        )

    def run(self):
        self.run_right_regular()
        self.run_holomorph()
        self.run_build_auto()

        return self.automorphism
