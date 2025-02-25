from pydantic import BaseModel
from enum import Enum
from fractions import Fraction
from typing import List, Set, Dict, Union

from algebra.number.types import Number, NumberType
from algebra.number.util import factorize


class Searcher:
    def __init__(self):
        self.start = None
        self.end = None

    def is_far(self):
        return (
            self.start is None or self.end is None or
            self.start + 1 < self.end
        )

    def get_middle(self):
        if self.start is None:
            if self.end is None:
                return 0
            elif self.end == 0:
                return -1
            else:
                return self.end * 2
        elif self.end is None:
            if self.start == 0:
                return 1
            else:
                return self.start * 2
        else:
            return (self.start + self.end) // 2

    def move_up(self):
        self.start = self.get_middle()

    def move_down(self):
        self.end = self.get_middle()

    def show(self):
        pass


class Sign(Enum):
    POSITIVE = 1
    ZERO = 2
    NEGATIVE = 3

    @classmethod
    def from_number(cls, number):
        if number > 0:
            return cls.POSITIVE
        elif number == 0:
            return cls.ZERO
        else:
            return cls.NEGATIVE


class Radical(BaseModel):
    body: List['RadicalElement'] = field(default_factory=list)

    @classmethod
    def from_num(cls, number: Number):
        return cls(body=[RadicalElement(number)])

    @classmethod
    def sqrt(cls, number):
        base_list = []
        multiply = 1
        for p, e in factorize(number).items():
            multiply *= pow(p, e // 2)
            if e % 2 == 1:
                base_list.append(p)

        return cls(
            body=[
                RadicalElement(
                    multiply=multiply, base_split=set(base_list)
                )
            ]
        )

    def __neg__(self):
        return Radical(body=[-e for e in self.body])

    def __add__(self, other):
        return self._normalize(self.body + other.body)

    def __sub__(self, other):
        return self._normalize(
            self.body + [
                -elem for elem in self._get_body(other)
            ]
        )

    def __mul__(self, other):
        return self._normalize([
            e1 * e2
            for e2 in self._get_body(other)
            for e1 in self.body
        ])

    def __truediv__(self, other: Union['Radical', Number]):
        if isinstance(other, Radical):
            return self * other.inv()
        else:
            return self._normalize([
                elem / other
                for elem in self.body
            ])

    def __gt__(self, other):
        return (self - other).get_sign() == Sign.POSITIVE

    def __eq__(self, other):
        return (self - other).get_sign() == Sign.ZERO

    def is_positive(self):
        return self.get_sign() == Sign.POSITIVE

    def get_sign(self):
        prime = self._get_any_prime()
        if prime is None:
            for element in self.body:
                return Sign.from_number(element.multiply)
            return Sign.ZERO

        a = Radical()
        b = Radical()
        for element in self.body:
            copied = element.copy_exclude(prime)
            if prime in element.base_split:
                b.body.append(copied)
            else:
                a.body.append(copied)

        a_sign = a.get_sign()
        b_sign = b.get_sign()

        if a_sign == b_sign:
            return a_sign

        elif a_sign == Sign.ZERO:
            return b_sign
        elif b_sign == Sign.ZERO:
            return a_sign

        determine = a * a - b * b * prime

        if a_sign == Sign.POSITIVE and b_sign == Sign.NEGATIVE:
            return determine.get_sign()
        elif a_sign == Sign.NEGATIVE and b_sign == Sign.POSITIVE:
            return (-determine).get_sign()

        raise ValueError("Unreachable")

    def ceil(self):
        searcher = Searcher()
        while searcher.is_far():
            searcher.show()
            middle = searcher.get_middle()
            if self > middle:
                searcher.move_up()
            elif self == middle:
                return middle
            else:
                searcher.move_down()
        return searcher.get_middle()

    def inv(self):
        if len(self.body) == 0:
            raise ZeroDivisionError('Zero')

        current = self
        inverse = self.from_num(1)

        while True:
            prime = current._get_any_prime()
            if prime is None:
                inverse /= current._get_constant()
                break

            a = Radical()
            b = Radical()

            for e in current.body:
                if prime in e.base_split:
                    b.body.append(e.copy())
                else:
                    a.body.append(e.copy())

            inverse *= a - b
            current = a * a - b * b

        return inverse

    def _normalize(self, body_list: List['RadicalElement']):
        base: Dict[int, RadicalElement] = {}
        for element in body_list:
            if element.base_number in base:
                base[element.base_number].multiply += element.multiply
            else:
                base[element.base_number] = element.copy()

        return Radical(body=[
            element
            for element in base.values()
            if element.multiply != 0
        ])

    def _get_body(self, other):
        if isinstance(other, int):
            return [RadicalElement(multiply=other)]
        elif isinstance(other, Radical):
            return other.body
        else:
            return []

    def _get_any_prime(self):
        for element in self.body:
            for prime in element.base_split:
                return prime

    def _get_constant(self):
        for element in self.body:
            if len(element.base_split) == 0:
                return element.multiply


class RadicalElement(BaseModel):
    multiply: Number  # will be normalized to Fraction.
    base_split: Set[int] = field(default_factory=set)

    def __post_init__(self):
        if not isinstance(self.multiply, Fraction):
            self.multiply = Fraction(self.multiply)

    @property
    def base_number(self):
        number = 1
        for base in self.base_split:
            number *= base
        return number

    def copy(self):
        return RadicalElement(
            multiply=self.multiply,
            base_split=set(self.base_split)
        )

    def copy_exclude(self, prime):
        bs = set(self.base_split)
        bs.discard(prime)
        return RadicalElement(multiply=self.multiply, base_split=bs)

    def __neg__(self):
        return RadicalElement(
            multiply=-self.multiply,
            base_split=set(self.base_split)
        )

    def __mul__(self, other):
        self_set = set(self.base_split)
        multiply = self.multiply * other.multiply
        for base in other.base_split:
            if base in self_set:
                self_set.remove(base)
                multiply *= base
            else:
                self_set.add(base)
        return RadicalElement(multiply=multiply, base_split=self_set)

    def __truediv__(self, other: Number):
        assert isinstance(other, NumberType), type(other)

        return RadicalElement(
            multiply=self.multiply / other,
            base_split=set(self.base_split)
        )
