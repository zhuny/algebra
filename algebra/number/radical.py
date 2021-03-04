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

    def __eq__(self, other):
        return (self - other).is_zero()

    def __add__(self, other):
        if isinstance(other, NumberType):
            other = self.from_number(other)
        assert isinstance(other, Radical)

        return Radical(
            constant=self.constant+other.constant,
            body=self.body+other.body
        )

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        return Radical(
            constant=-self.constant,
            body=[-x for x in self.body]
        )

    def is_zero(self):
        # TODO: self.body가 normalize되면서 0이 되는 경우는 나중에
        return self.constant == 0 and len(self.body) == 0


@dataclass
class RadicalElement:
    multiplier: Fraction
    index: int
    radicand: Radical
