from typing import Iterator, Container

from typing_extensions import Generic, TypeVar

from algebra2.exception import WorkInProgressError
from algebra2.group.base import GroupRepresentation, GroupElement, GroupDefinition


# 앞으로 나올 3개를 서로 묶을 타입 변수
R = TypeVar("R", bound="PermutationGroupRepresentation")  # representation 타입
E = TypeVar("E", bound="PermutationGroupElement")         # element 타입
G = TypeVar("G", bound="PermutationGroupDefinition")      # group 타입
O = TypeVar("O", bound="PermutationGroupObject")


class PermutationGroupRepresentation(GroupDefinition[R, E, G],
                                     Generic[R, E, G, O]):
    def iter_objects(self) -> Iterator[O]:
        raise NotImplementedError(type(self))

    def degree(self) -> int:
        raise NotImplementedError(type(self))


class PermutationGroupElement(GroupDefinition[R, E, G],
                              Generic[R, E, G, O]):
    data: dict[O, O]

    def act(self, obj: O) -> O:
        return self.data.get(obj, obj)

    def cycles(self) -> list[list[O]]:
        raise WorkInProgressError()

    def sign(self) -> int:
        raise WorkInProgressError()


class PermutationGroupDefinition(GroupDefinition[R, E, G],
                                 Generic[R, E, G, O]):
    def orbit(self, obj: O) -> list[O]:
        raise WorkInProgressError()

    def orbits(self) -> list[list[O]]:
        raise WorkInProgressError()

    def stabilizer(self, obj: O) -> G:
        raise WorkInProgressError()

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


class PermutationGroupObject(Generic[R, E, G, O]):
    pass
