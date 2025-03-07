from typing import Any, Self

import pydantic

from algebra.ring.polynomial.monomial_ordering import \
    GradedReverseLexicographicOrdering, MonomialOrderingBase
from algebra.ring.polynomial.naming import VariableNameIndexGenerator, \
    VariableNameGenerator, VariableNameListGenerator
from algebra.util.model import AlgebraModelBase


class VariableSystemBase(AlgebraModelBase):
    def get_name(self, index: int) -> str:
        raise NotImplementedError(self)

    def get_key(self, monomial) -> Any:
        raise NotImplementedError(self)

    def get_size(self):
        raise NotImplementedError(self)

    def register_variable(self, container, variable_iter):
        raise NotImplementedError(self)


class VariableSystem(VariableSystemBase):
    naming: None | int | str | VariableNameGenerator = None
    ordering: MonomialOrderingBase = pydantic.Field(
        default_factory=GradedReverseLexicographicOrdering
    )

    @pydantic.model_validator(mode='before')
    @classmethod
    def wrap_ordering(cls, data):
        if data.get('ordering') is None:
            data.pop('ordering', None)
        return data

    # @pydantic.model_validator(mode='after')
    # def wrap_naming(self) -> Self:
    #     return self.model_copy(update={
    #         'naming': self._wrap_naming(self.naming)
    #     })

    @pydantic.field_validator('naming', mode='before')
    @classmethod
    def wrap_naming(cls, naming) -> VariableNameGenerator:
        if naming is None:
            return VariableNameListGenerator(name_list=['x'])
        elif isinstance(naming, int):
            if naming == 1:
                return VariableNameListGenerator(name_list=['x'])
            else:
                return VariableNameIndexGenerator(name='x', size=naming)
        elif isinstance(naming, str):
            return VariableNameListGenerator(name_list=naming)
        elif isinstance(naming, VariableNameGenerator):
            return naming
        else:
            raise TypeError(naming)

    def get_name(self, index: int) -> str:
        return self.naming.get(index)

    def get_key(self, monomial) -> Any:
        return self.ordering.key(monomial)

    def get_size(self):
        return self.naming.get_size()

    def register_variable(self, container, variable_iter):
        self.naming.register_variable(container, variable_iter)


class CombineVariableSystem(VariableSystemBase):
    system_list: list[
        VariableSystemBase | VariableNameGenerator | MonomialOrderingBase
    ]

    @pydantic.field_validator('system_list', mode='before')
    @classmethod
    def wrap_system_list(cls, system_list):
        return [cls._wrap_system(system) for system in system_list]

    @staticmethod
    def _wrap_system(system):
        if isinstance(system, VariableSystemBase):
            return system
        elif isinstance(system, VariableNameGenerator):
            return VariableSystem(naming=system)
        elif isinstance(system, MonomialOrderingBase):
            return VariableSystem(ordering=system)
        else:
            raise TypeError(system)

    def get_name(self, index: int) -> str:
        # 아마 BST를 하면 더 좋겠지만 일단 넘어가기로 한다.
        for system in self.system_list:
            size = system.get_size()
            if 0 <= index < size:
                return system.get_name(index)
            index -= size

    def get_key(self, monomial) -> Any:
        return tuple(
            system.get_key(monomial) for system in self.system_list
        )

    def get_size(self):
        return sum(
            system.get_size() for system in self.system_list
        )

    def register_variable(self, container, variable_iter):
        for system in self.system_list:
            system.register_variable(container, variable_iter)


class VariableContainer:
    def __init__(self):
        self._variable_dict = {}
        self._variable_list = []

    def __iter__(self):
        return iter(self._variable_list)

    def __getattr__(self, item):
        return self._variable_dict[item]

    def set(self, name, variable):
        self._variable_dict[name] = variable
        self._variable_list.append(variable)

    def set_many(self, name, variable_list):
        self._variable_dict[name] = tuple(variable_list)
        self._variable_list.extend(variable_list)
