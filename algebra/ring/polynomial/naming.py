import pydantic

from algebra.util.model import AlgebraModelBase


class VariableNameGenerator(AlgebraModelBase):
    def get(self, index: int) -> str:
        raise NotImplementedError(self)

    def get_size(self):
        raise NotImplementedError(self)

    def register_variable(self, container, variable_iter):
        raise NotImplementedError(self)


class VariableNameListGenerator(VariableNameGenerator):
    name_list: list[str]

    @pydantic.field_validator('name_list', mode='before')
    @classmethod
    def str_to_list(cls, value) -> list[str]:
        if isinstance(value, str):
            return list(value)
        else:
            return value

    def get(self, index) -> str:
        return self.name_list[index]

    def get_size(self):
        return len(self.name_list)

    def register_variable(self, container, variable_iter):
        for name in self.name_list:
            container.set(name, next(variable_iter))


class VariableNameIndexGenerator(VariableNameGenerator):
    def __init__(self, name, size=3):
        self.name = name
        self.size = size

    def get(self, index: int) -> str:
        return f'{self.name}{index}'

    def get_size(self):
        return self.size

    def register_variable(self, container, variable_iter):
        this_variable = [
            next(variable_iter)
            for _ in range(self.size)
        ]
        container.set_many(self.name, this_variable)
