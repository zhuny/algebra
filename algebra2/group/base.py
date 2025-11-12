import itertools
import re
from typing import TypeVar, Any, Iterator, Type

from pydantic import BaseModel, ConfigDict
from typing_extensions import Generic


# 앞으로 나올 3개를 서로 묶을 타입 변수
R = TypeVar("R", bound="GroupRepresentation")  # representation 타입
E = TypeVar("E", bound="GroupElement")         # element 타입
G = TypeVar("G", bound="GroupDefinition")      # group 타입


class AppBaseModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class GroupRepresentation(AppBaseModel, Generic[R, E, G]):
    def element(self, *args, **kwargs) -> E:
        raise NotImplementedError(type(self))

    def identity(self) -> E:
        raise NotImplementedError(type(self))

    def group(self, generator_list: list[Any], name=None, **kwargs) -> G:
        generator_list = [self.element(e) for e in generator_list]
        return self.group_cls()(
            representation=self,
            generator_list=generator_list,
            name=name,
            **kwargs
        )

    def group_cls(self) -> Type[G]:
        raise NotImplementedError(type(self))


class GroupElement(AppBaseModel, Generic[R, E, G]):
    representation: R

    def __mul__(self: E, other: E) -> E:
        raise NotImplementedError(type(self))

    def __truediv__(self: E, other: E) -> E:
        raise NotImplementedError(type(self))

    def __pow__(self, power: int, modulo=None) -> E:
        if modulo is not None:
            raise ValueError("'modulo' is not supported")

        result = self.representation.identity()

        if power == 0:
            return result

        base = self
        if power < 0:
            base = base.inverse()
            power = -power

        while power > 0:
            if power % 2 == 0:
                result *= base

            power >>= 1
            base = base * base

        return base

    def conjugate(self: E, element: E) -> E:
        return element * self * element.inverse()

    def inverse(self) -> E:
        raise NotImplementedError(type(self))

    def order(self) -> int:
        raise NotImplementedError(type(self))

    def is_identity(self) -> bool:
        raise NotImplementedError(type(self))


class GroupDefinition(AppBaseModel, Generic[R, E, G]):
    representation: R
    name: str | None = None
    generator_list: list[E]

    @classmethod
    def cls_name(cls):
        return "".join(re.findall(r"[A-Z]", cls.__name__))

    def __repr__(self):
        additional = "" if self.name is None else ", " + self.name
        return f"{self.cls_name()}({self.generator_list}{additional})"

    __str__ = __repr__

    def __contains__(self, element: E) -> bool:
        return element in self

    def order(self) -> int:
        raise NotImplementedError(type(self))

    def is_abelian(self) -> bool:
        for e1, e2 in itertools.combinations(self.generator_list, 2):
            if e1 * e2 != e2 * e1:
                return False
        return True

    def contains(self, element: E) -> bool:
        raise NotImplementedError(type(self))

    def is_subgroup(self, subgroup: G) -> bool:
        for element in subgroup.generator_list:
            if not self.contains(element):
                return False
        return True

    def iter_elements(self) -> Iterator[E]:
        raise NotImplementedError(type(self))

    def random_element(self) -> E:
        raise NotImplementedError(type(self))

    def centralizer(self, element: E) -> G:
        raise NotImplementedError(type(self))

    def normalizer(self, subgroup: G) -> G:
        raise NotImplementedError(type(self))

    def is_normalizer(self, element: E) -> bool:
        for g in self.generator_list:
            conj = element * g / element
            if not self.contains(conj):
                return False
        return True

    def automorphism_group(self):
        raise NotImplementedError(type(self))
