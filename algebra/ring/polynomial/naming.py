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


class VariableCombineGenerator(VariableNameGenerator):
    def __init__(self, info_list):
        start = 0
        self.info_list = []
        for limit, gen in info_list:
            self.info_list.append((start, gen))
            start += limit
        self.info_list.reverse()

        self.limit = start

    def get(self, index: int) -> str:
        for start, gen in self.info_list:
            if start <= index:
                return gen.get(index - start)

    def check_range(self, length: int) -> bool:
        return length <= self.limit
