from dataclasses import dataclass
from fractions import Fraction

from algebra.field.base import Field, FieldElement


@dataclass
class RationalField(Field):
    def element(self, value) -> 'FieldElement':
        return RationalFieldElement(field=self, value=Fraction(value))


@dataclass(eq=False)
class RationalFieldElement(FieldElement):
    value: Fraction

    def __str__(self):
        return str(self.value)

    def __add__(self, other):
        if isinstance(other, (int, Fraction)):
            return self._wrap(self.value + other)
        elif isinstance(other, RationalFieldElement):
            self._check_type(other)
            return self._wrap(self.value + other.value)
        else:
            return NotImplemented

    def __radd__(self, other):
        return self + other

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

    def __rmul__(self, other):
        return self * other

    def inv(self):
        return self._wrap(1 / self.value)

    def __eq__(self, other):
        left, right = self._wrap_compare(other)
        return left == right

    def is_zero(self):
        return self.value == 0

    def is_one(self):
        return self.value == 1

    def _wrap(self, number):
        return RationalFieldElement(field=self.field, value=Fraction(number))

    def _check_type(self, other):
        if self.field != other.field:
            raise ValueError(
                "RationalFieldElement does not have the same field")

    def __gt__(self, other):
        left, right = self._wrap_compare(other)
        return left > right

    def _wrap_compare(self, other):
        other_value = other
        if isinstance(other, RationalFieldElement):
            other_value = other.value

        return self.value, other_value
