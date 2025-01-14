class VariableNameGenerator:
    def get(self, index: int) -> str:
        raise NotImplementedError(self)

    def get_size(self):
        raise NotImplementedError(self)

    def register_variable(self, container, variable_iter):
        raise NotImplementedError(self)


class VariableNameListGenerator(VariableNameGenerator):
    def __init__(self, name_list: str | list[str]):
        # name_list가 str인 경우 한 글자씩 분리됩니다.
        self.name_list: list[str] = list(name_list)

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
