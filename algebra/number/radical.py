import functools
import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import List

from algebra.number.types import Number, NumberType


@dataclass(eq=False)
class Radical:
    constant: Fraction
    body: List['RadicalElement'] = field(default_factory=list)

    @classmethod
    def from_number(cls, n: Number):
        """
        :param n: Any Number value supported by Fraction.
            Float is not recommended
        :return: Radical object
        """
        return cls(constant=Fraction(n))

    @classmethod
    def _wrap(cls, other):
        if isinstance(other, NumberType):
            return cls.from_number(other)
        assert isinstance(other, Radical)
        return other

    def __eq__(self, other):
        return (self - other).is_zero()

    def __add__(self, other):
        other = self._wrap(other)

        return Radical(
            constant=self.constant+other.constant,
            body=self.body+other.body
        )

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        other = self._wrap(other)
        body = [b1 * other.constant for b1 in self.body]
        body += [b2 * self.constant for b2 in other.body]
        body += [
            b1 * b2
            for b1 in self.body for b2 in other.body
        ]
        return Radical(
            constant=self.constant*other.constant,
            body=body
        )

    def __neg__(self):
        return Radical(
            constant=-self.constant,
            body=[-x for x in self.body]
        )

    def __pow__(self, power, modulo=None):
        assert isinstance(power, int)  # TODO: 나중에 Fraction도 고려
        assert power >= 0  # TODO: 음수도 고려...

        multiplier_list = []
        current = self
        while power > 0:
            if power % 2 == 1:
                multiplier_list.append(current)
            power >>= 1
            current = current * current

        if len(multiplier_list) == 0:
            return Radical.from_number(1)
        else:
            return functools.reduce(lambda x, y: x*y, multiplier_list)

    def is_zero(self):
        # TODO: self.body가 normalize되면서 0이 되는 경우는 나중에
        return self.constant == 0 and len(self.body) == 0

    def sqrt(self):
        # TODO: 대신 simplied 해야 됨
        return Radical(
            constant=Fraction(),
            body=[
                RadicalElement(
                    multiplier=Fraction(1), index=2,
                    radicand=self
                )
            ]
        )


@dataclass
class RadicalElement:
    multiplier: Fraction
    index: int
    radicand: Radical

    def __neg__(self):
        return RadicalElement(
            multiplier=-self.multiplier,
            index=self.index,
            radicand=self.radicand
        )

    def __mul__(self, other):
        if isinstance(other, NumberType):
            return RadicalElement(
                multiplier=self.multiplier * other,
                index=self.index,
                radicand=self.radicand * (other ** self.index)
            )
        assert isinstance(other, RadicalElement), type(other)  # FIXME: 다른게 오게 될 수도?
        g = math.gcd(self.index, other.index)
        return RadicalElement(
            multiplier=self.multiplier*other.multiplier,
            index=self.index*other.index//g,
            radicand=(
                (self.radicand ** (other.index//g)) *
                (other.radicand ** (self.index//g))
            )
        )
