from pydantic import BaseModel

from algebra.field.base import Field, FieldElement
from algebra.number.util import is_prime


class FinitePrimeField(Field):
    char: int

    def model_post_init(self, __context):
        if not is_prime(self.char):
            raise ValueError("Prime should be given")

    def element(self, number) -> 'FieldElement':
        if isinstance(number, int):
            return FinitePrimeFieldElement(field=self, value=number % self.char)
        elif isinstance(number, FinitePrimeFieldElement):
            if number.field == self:
                return number
            else:
                raise ValueError("field not matched")

        raise ValueError("Invalid element")

    def size(self):
        # extended field의 경우 power가 곱해진 값일 것이다.
        return self.char

    def get_char(self):
        return self.char


class FinitePrimeFieldElement(FieldElement):
    field: FinitePrimeField
    value: int

    def __str__(self):
        return str(self.value)

    def __add__(self, other):
        if not self._is_valid_value(other):
            return NotImplemented

        return self._wrap_result(self.value + self._wrap_value(other))

    __radd__ = __add__

    def __neg__(self):
        return self._wrap_result(-self.value)

    def __mul__(self, other):
        if not self._is_valid_value(other):
            return NotImplemented

        return self._wrap_result(self.value * self._wrap_value(other))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other):
        return (
            self._is_valid_value(other) and
            self.value == self._wrap_value(other)
        )

    def __pow__(self, power):
        if not isinstance(power, int):
            raise ValueError("Power should be integer")
        if power < 0:
            if self.is_zero():
                raise ValueError("Zero power not allowed")

            base = self.inv()
        else:
            base = self

        return self._wrap_result(pow(base.value, power, self.field.char))

    def inv(self):
        if self.field.char <= 3:
            return self._wrap_result(self.value)

        char = self.field.char
        return self._wrap_result(pow(self.value, char - 2, char))

    def is_zero(self):
        return self.value == 0

    def is_one(self):
        return self.value == 1

    def convert(self, another):
        return another.element(self.value)

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
