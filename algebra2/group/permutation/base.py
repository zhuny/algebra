from typing import Iterator, Container, Any, Union, Type

from pydantic import BaseModel, field_validator
from typing_extensions import Generic, TypeVar

from algebra2.exception import WorkInProgressError
from algebra2.group.base import GroupRepresentation, GroupElement, GroupDefinition, AppBaseModel

# 앞으로 나올 4개를 서로 묶을 타입 변수
R = TypeVar("R", bound="PermutationGroupRepresentation")  # representation 타입
E = TypeVar("E", bound="PermutationGroupElement")         # element 타입
G = TypeVar("G", bound="PermutationGroupDefinition")      # group 타입
O = TypeVar("O", bound="PermutationGroupObject")          # object 타입


class PermutationGroupRepresentation(GroupRepresentation[R, E, G],
                                     Generic[R, E, G, O]):
    def iter_objects(self) -> Iterator[O]:
        raise NotImplementedError(type(self))

    def degree(self) -> int:
        raise NotImplementedError(type(self))

    def object(self, *args, **kwargs) -> O:
        raise NotImplementedError(type(self))

    def element_cls(self) -> Type[E]:
        raise NotImplementedError(type(self))

    def element(self,
                cycle_info: Union[
                    list[list[int | O]],
                    dict[O, O],
                    E
                ]) -> E:
        mapping = {}
        element_cls: Type[E] = self.element_cls()

        if isinstance(cycle_info, element_cls):
            if self != cycle_info.representation:
                raise ValueError("Representation not matched")
            return cycle_info

        elif isinstance(cycle_info, dict):
            for k, v in cycle_info.items():
                k, v = self.object(k), self.object(v)
                mapping[k] = v

        elif isinstance(cycle_info, list):
            for cycle in cycle_info:
                cycle = [self.object(obj) for obj in cycle]

                if len(set(cycle)) != len(cycle):
                    raise TypeError

                mapping.update(zip(cycle, cycle[1:] + cycle[:1]))

        else:
            raise TypeError(f"Unknown type : {type(cycle_info)}")

        return element_cls(representation=self, data=mapping)


class PermutationGroupElement(GroupElement[R, E, G],
                              Generic[R, E, G, O]):
    data: dict[O, O]

    @field_validator("data")
    @classmethod
    def _remove_same_items(cls, data):
        return {
            k: v
            for k, v in data.items()
            if k != v
        }

    def __truediv__(self, other: E) -> E:
        return self * other.inverse()

    def inverse(self) -> E:
        return self.representation.element({
            v: k
            for k, v in self.data.items()
        })

    def act(self, obj: O) -> O:
        return self.data.get(obj, obj)

    def cycles(self) -> list[list[O]]:
        raise WorkInProgressError()

    def sign(self) -> int:
        raise WorkInProgressError()

    def is_identity(self) -> bool:
        return len(self.data) == 0


class PermutationGroupDefinition(GroupDefinition[R, E, G],
                                 Generic[R, E, G, O]):
    def orbit(self, obj: Any) -> list[O]:
        obj: O = self.representation.object(obj)
        orbit_set = set()
        queue = [obj]

        while queue:
            current = queue.pop()
            if current in orbit_set:
                continue
            orbit_set.add(current)

            for element in self.generator_list:
                other = element.act(current)
                queue.append(other)

        return list(orbit_set)

    def orbits(self) -> list[list[O]]:
        raise WorkInProgressError()

    def stabilizer(self, obj: Any) -> G:
        obj: O = self.representation.object(obj)
        queue = [obj]
        done = set()
        transversal = {obj: self.representation.identity()}
        new_generator = []

        while queue:
            current = queue.pop()
            if current in done:
                continue
            done.add(current)

            for g in self.generator_list:
                other = g.act(current)
                if other not in transversal:
                    transversal[other] = transversal[current] * g
                    queue.append(other)
                else:
                    new_generator.append(
                        transversal[current] * g / transversal[other]
                    )

        return self.representation.group(
            generator_list=new_generator,
            name=(
                None if self.name is None else
                f"Stab({self.name}, {obj})"
            )
        )

    def stabilizer_set_wise(self, obj_set: Container[O]) -> G:
        raise WorkInProgressError()

    def stabilizer_point_wise(self, obj_set: Container[O]) -> G:
        raise WorkInProgressError()

    def stabilizer_chain(self):
        raise WorkInProgressError()

    def is_transitive(self) -> bool:
        for obj in self.representation.iter_objects():
            obj_orbit = self.orbit(obj)
            return len(obj_orbit) == self.representation.degree()

        # 사실상 unreachable
        return False


class PermutationGroupObject(AppBaseModel, Generic[R, E, G, O]):
    representation: R
