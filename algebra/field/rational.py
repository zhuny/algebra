from dataclasses import dataclass
from fractions import Fraction

from algebra.field.base import Field, FieldElement


@dataclass
class RationalField(Field):
    def element(self, value) -> 'FieldElement':
        return RationalFieldElement(field=self, value=Fraction(value))

    def zero(self):
        return self.element(0)

    def one(self):
        return self.element(1)


@dataclass(eq=False)
class RationalFieldElement(FieldElement):
    value: Fraction

    def __add__(self, other):
        return self._wrap(self.value + other.value)

    def __neg__(self):
        return self._wrap(-self.value)

    def __mul__(self, other):
        if isinstance(other, (int, Fraction)):
            return self._wrap(self.value * other)
        elif isinstance(other, RationalFieldElement):
            self._check_type(other)
            return self._wrap(self.value * other.value)
        else:
            return NotImplemented

    def inv(self):
        return self._wrap(1 / self.value)

    def __eq__(self, other):
        if isinstance(other, RationalFieldElement):
            return self.value == other.value
        else:
            return self.value == other

    def is_zero(self):
        return self.value == 0

    def _wrap(self, number):
        return RationalFieldElement(field=self.field, value=Fraction(number))

    def _check_type(self, other):
        if self.field != other.field:
            raise ValueError(
                "RationalFieldElement does not have the same field")
