from typing import Any

from algebra.ring.polynomial.monomial_ordering import \
    GradedReverseLexicographicOrdering, MonomialOrderingBase
from algebra.ring.polynomial.naming import VariableNameIndexGenerator, \
    VariableNameGenerator, VariableNameListGenerator


class VariableSystemBase:
    def get_name(self, index: int) -> str:
        raise NotImplementedError(self)

    def get_key(self, monomial) -> Any:
        raise NotImplementedError(self)

    def get_size(self):
        raise NotImplementedError(self)

    def register_variable(self, container, variable_iter):
        raise NotImplementedError(self)


class VariableSystem(VariableSystemBase):
    def __init__(self,
                 naming: None | int | str | VariableNameGenerator = None,
                 ordering=None):
        self.naming = self._wrap_naming(naming)
        self.ordering = ordering or GradedReverseLexicographicOrdering()

    def _wrap_naming(self, naming) -> VariableNameGenerator:
        if naming is None:
            return VariableNameListGenerator('x')
        elif isinstance(naming, int):
            return VariableNameIndexGenerator('x', naming)
        elif isinstance(naming, str):
            return VariableNameListGenerator(naming)
        elif isinstance(naming, VariableNameGenerator):
            return naming
        else:
            raise NotImplementedError(naming)

    def get_name(self, index: int) -> str:
        return self.naming.get(index)

    def get_key(self, monomial) -> Any:
        return self.ordering.key(monomial)

    def get_size(self):
        return self.naming.get_size()

    def register_variable(self, container, variable_iter):
        self.naming.register_variable(container, variable_iter)


class CombineVariableSystem(VariableSystemBase):
    def __init__(self,
                 system_list: list[VariableSystemBase |
                                   VariableNameGenerator |
                                   MonomialOrderingBase]):
        self.system_list = [
            self._wrap_system(system)
            for system in system_list
        ]

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
