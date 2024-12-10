from dataclasses import dataclass
from fractions import Fraction

from algebra.field.base import Field, FieldElement


class RationalField(Field):
    def element(self, value) -> 'FieldElement':
        return RationalFieldElement(field=self, value=value)


@dataclass
class RationalFieldElement(FieldElement):
    value: Fraction

    def __add__(self, other):
        return self._wrap_value(self.value + other.value)

    def __neg__(self):
        return self._wrap_value(-self.value)

    def __mul__(self, other):
        return self._wrap_value(self.value * other.value)

    def inv(self):
        return self._wrap_value(1 / self.value)

    def _wrap_value(self, value):
        cls = type(self)
        return cls(field=self.field, value=value)
