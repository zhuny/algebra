from dataclasses import dataclass


@dataclass
class Field:
    def element(self, *args) -> 'FieldElement':
        raise NotImplementedError(self)

    def zero(self):
        raise NotImplementedError(self)

    def one(self):
        raise NotImplementedError(self)


@dataclass
class FieldElement:
    field: Field

    def __add__(self, other):
        raise NotImplementedError(self)

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        raise NotImplementedError(self)

    def __mul__(self, other):
        raise NotImplementedError(self)

    def __truediv__(self, other):
        return self * other.inv()

    def inv(self):
        raise NotImplementedError(self)

    def is_zero(self):
        raise NotImplementedError(self)

    def is_one(self):
        raise NotImplementedError(self)
