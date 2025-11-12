from typing import TypeVar, Type, Iterator

from pydantic import Field, model_validator

from algebra2.group.permutation.base import PermutationGroupRepresentation, PermutationGroupElement, \
    PermutationGroupObject, PermutationGroupDefinition

# 앞으로 나올 4개를 서로 묶을 타입 변수
R = TypeVar("R", bound="SimPermGrpRepresentation")  # representation 타입
E = TypeVar("E", bound="SimPermGrpElement")         # element 타입
G = TypeVar("G", bound="SimPermGrpDefinition")      # group 타입
O = TypeVar("O", bound="SimPermGrpObject")          # object 타입


class SimPermGrpRepresentation(PermutationGroupRepresentation[R, E, G, O]):
    this_degree: int = Field(alias="degree")

    def degree(self) -> int:
        return self.this_degree

    def object(self, num: int | O) -> O:
        if isinstance(num, int):
            num = SimPermGrpObject(representation=self, number=num)

        if num.representation != self:
            raise ValueError("Representation Not Matched")

        return num

    def group_cls(self) -> Type[G]:
        return SimPermGrpDefinition

    def element_cls(self) -> Type[E]:
        return SimPermGrpElement

    def identity(self) -> E:
        return self.element([])

    def iter_objects(self) -> Iterator[O]:
        for i in range(self.this_degree):
            yield self.object(i)


class SimPermGrpDefinition(PermutationGroupDefinition[R, E, G, O]):
    def direct_product(self, other: 'SimPermGrpDefinition'):
        first_degree = self.representation.this_degree
        rep = SimPermGrpRepresentation(degree=first_degree + other.representation.this_degree)
        element_list = [
            g.model_dump_data()
            for g in self.generator_list
        ]
        element_list.extend(
            g.model_dump_data(first_degree)
            for g in other.generator_list
        )
        return rep.group(element_list)


class SimPermGrpElement(PermutationGroupElement[R, E, G, O]):
    def __repr__(self):
        return repr(self.model_dump_data())

    def __hash__(self):
        items = list(self.model_dump_data().items())
        items.sort()
        items = tuple(items)
        return hash(items)

    def __mul__(self, other: E) -> E:
        self._check_type(other)

        other_map = dict(other.data)
        result = {}
        for k, v in self.data.items():
            result[k] = other_map.pop(v, v)
        result.update(other_map)

        return self.representation.element(result)

    def _check_type(self, other: E):
        if type(self) != type(other):
            # Strict check rather than isinstance
            raise TypeError("Type not matched")

        if self.representation != other.representation:
            raise ValueError("Representation not matched")

    def model_dump_data(self, offset=0):
        return {
            k.number + offset: v.number + offset
            for k, v in self.data.items()
        }


class SimPermGrpObject(PermutationGroupObject[R, E, G, O]):
    number: int

    @model_validator(mode="after")
    def check_number(self):
        if 0 <= self.number < self.representation.this_degree:
            return self

        raise ValueError("number range not corrected")

    def __repr__(self):
        return str(self.number)

    __str__ = __repr__


def cyclic_product(order_list: list[int]):
    rep = SimPermGrpRepresentation(degree=sum(order_list))

    element_list = []
    start = 0
    for order in order_list:
        end = start + order
        element_list.append([list(range(start, end))])
        start = end

    return rep.group(element_list)
