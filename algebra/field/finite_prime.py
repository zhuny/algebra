from dataclasses import dataclass

from algebra.field.base import Field, FieldElement
from algebra.number.util import is_prime


@dataclass
class FinitePrimeField(Field):
    char: int

    def __post_init__(self):
        if not is_prime(self.char):
            raise ValueError("Prime should be given")

    def element(self, number) -> 'FieldElement':
        return FinitePrimeFieldElement(self, number % self.char)


@dataclass
class FinitePrimeFieldElement(FieldElement):
    field: FinitePrimeField
    value: int

    def __add__(self, other):
        return self._wrap(self.value + other.value)

    def __neg__(self):
        return self._wrap(-self.value)

    def __mul__(self, other):
        return self._wrap(self.value * other.value)

    def inv(self):
        if self.field.char <= 3:
            return self._wrap(self.value)

        char = self.field.char
        return self._wrap(pow(self.value, char - 2, char))

    def is_zero(self):
        return self.value == 0

    def is_one(self):
        return self.value == 1

    def _wrap(self, value):
        return FinitePrimeFieldElement(
            field=self.field, value=value % self.field.char
        )
