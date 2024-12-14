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

    def __str__(self):
        return str(self.value)

    def __add__(self, other):
        if not self._is_valid_value(other):
            return NotImplemented

        return self._wrap_result(self.value + self._wrap_value(other))

    def __neg__(self):
        return self._wrap_result(-self.value)

    def __mul__(self, other):
        if not self._is_valid_value(other):
            return NotImplemented

        return self._wrap_result(self.value * self._wrap_value(other))

    def __eq__(self, other):
        return (
            self._is_valid_value(other) and
            self.value == self._wrap_value(other)
        )

    def inv(self):
        if self.field.char <= 3:
            return self._wrap_result(self.value)

        char = self.field.char
        return self._wrap_result(pow(self.value, char - 2, char))

    def is_zero(self):
        return self.value == 0

    def is_one(self):
        return self.value == 1

    @staticmethod
    def _is_valid_value(other):
        return isinstance(other, (FinitePrimeFieldElement, int))

    @staticmethod
    def _wrap_value(other):
        if isinstance(other, FinitePrimeFieldElement):
            return other.value
        elif isinstance(other, int):
            return other

    def _wrap_result(self, value):
        return FinitePrimeFieldElement(
            field=self.field, value=value % self.field.char
        )
