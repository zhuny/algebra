from pydantic import BaseModel
from fractions import Fraction

from algebra.field.base import Field, FieldElement
from algebra.number.util import is_square, is_square_free


class RationalField(Field):
    def element(self, value) -> 'FieldElement':
        if isinstance(value, RationalFieldElement):
            return value
        return RationalFieldElement(field=self, value=Fraction(value))

    def get_char(self):
        # 무한대의 경우 항상 0을 반환한다.
        return 0


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

    def __mod__(self, other):
        return self.value % other

    def is_zero(self):
        return self.value == 0

    def is_one(self):
        return self.value == 1

    def convert(self, field):
        return field.element(int(self.value))

    def _wrap(self, number):
        return RationalFieldElement(field=self.field, value=Fraction(number))

    def _check_type(self, other):
        if self.field != other.field:
            raise ValueError(
                "RationalFieldElement does not have the same field")

    def __gt__(self, other):
        left, right = self._wrap_compare(other)
        return left > right

    def is_square(self):
        v = self.value
        return is_square(v.numerator * v.denominator)

    def is_square_free(self):
        v = self.value
        return is_square_free(v.numerator * v.denominator)

    def _wrap_compare(self, other):
        other_value = other
        if isinstance(other, RationalFieldElement):
            other_value = other.value

        return self.value, other_value
