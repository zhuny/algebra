class VariableNameGenerator:
    def get(self, index: int) -> str:
        raise NotImplementedError(self)

    def check_range(self, length: int) -> bool:
        raise NotImplementedError(self)


class VariableNameListGenerator(VariableNameGenerator):
    def __init__(self, name_list):
        self.name_list: list[str] = list(name_list)

    def get(self, index) -> str:
        return self.name_list[index]

    def check_range(self, length) -> bool:
        return length <= len(self.name_list)


class VariableNameIndexGenerator(VariableNameGenerator):
    def __init__(self, name):
        self.name = name

    def get(self, index: int) -> str:
        return f'{self.name}{index}'

    def check_range(self, length) -> bool:
        return True
