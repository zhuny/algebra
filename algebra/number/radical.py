import collections
import functools
import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import List

from algebra.number.types import Number, NumberType
from algebra.number.util import factorize, lcm


@dataclass(eq=False, frozen=True, unsafe_hash=True)
class Radical:
    inv: int  # should be positive integer
    body: 'SimpleRadical'

    def __post_init__(self):
        if self.inv == 0:
            raise ValueError("Zero division?")
        if self.inv < 0:
            raise ValueError("Normalize to zero")

    @classmethod
    def from_number(cls, n: Number):
        """
        :param n: Any Number value supported by Fraction.
            Float is not recommended
        :return: Radical object
        """
        return cls(inv=n.denominator, body=SimpleRadical(n.numerator))

    def __eq__(self, other):
        return (self - other).is_zero()

    def __add__(self, other):
        if isinstance(other, NumberType):
            other = self.from_number(other)
        assert isinstance(other, Radical)

        return Radical(
            inv=self.inv * other.inv,
            body=self.body * other.inv + other.body * self.inv
        )._fast_simplify()

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if isinstance(other, NumberType):
            other = self.from_number(other)

        return Radical(
            inv=self.inv * other.inv,
            body=self.body * other.body
        )._fast_simplify()

    def __floordiv__(self, other):
        return self // other

    def __truediv__(self, other):
        if isinstance(other, int):
            return Radical(inv=self.inv*other, body=self.body)
        # FIXME: 다양한 경우에 대해서 고려해보자

    def __neg__(self):
        return Radical(inv=self.inv, body=-self.body)

    def _fast_simplify(self):
        body = self.body._fast_simplify()
        nums = [self.inv]
        if body.constant:
            nums.append(abs(body.constant))
        for sub_body in body.body:
            nums.append(abs(sub_body.multiplier))
        if len(nums) > 1:
            d = functools.reduce(math.gcd, nums)
            return Radical(inv=self.inv // d, body=body / d)
        else:
            return Radical(inv=self.inv, body=body)

    def is_zero(self):
        return self.body.is_zero()

    def sqrt(self):
        return Radical(
            inv=self.inv,
            body=(self.body*self.inv).sqrt()
        )._fast_simplify()

    def to_wolfram_alpha(self):
        upper = self.body.to_wolfram_alpha()
        if self.inv == 1:
            return upper
        else:
            return f"({upper})/{self.inv}"


@dataclass(eq=False, frozen=True)
class SimpleRadical:
    constant: int
    body: List['SimpleRadicalElement'] = field(default_factory=list)

    @classmethod
    def _wrap(cls, other):
        if isinstance(other, int):
            return SimpleRadical(constant=other)
        assert isinstance(other, SimpleRadical)
        return other

    def __hash__(self):
        return hash((
            self.constant,
            tuple(sorted(self.body, key=hash))
        ))

    def __eq__(self, other):
        return (self - other).is_zero()

    def __add__(self, other):
        other = self._wrap(other)

        return SimpleRadical(
            constant=self.constant+other.constant,
            body=self.body+other.body
        )

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        other = self._wrap(other)
        body = []
        if other.constant:
            body += [b1 * other.constant for b1 in self.body]
        if self.constant:
            body += [b2 * self.constant for b2 in other.body]
        body += [
            b1 * b2
            for b1 in self.body for b2 in other.body
        ]
        return SimpleRadical(
            constant=self.constant*other.constant,
            body=body
        )

    def __truediv__(self, other):
        assert isinstance(other, int)
        return SimpleRadical(
            constant=self.constant // other,
            body=[body / other for body in self.body]
        )

    def __neg__(self):
        return SimpleRadical(
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
            return SimpleRadical.from_number(1)
        else:
            return functools.reduce(lambda x, y: x*y, multiplier_list)

    def _fast_simplify(self):
        const = self.constant
        body_map = collections.defaultdict(int)
        body_rest = []

        for body in self.body:
            body = body._fast_simplify()
            if body.radicand._is_integer():
                if body._is_integer():
                    const += body.multiplier
                else:
                    key = body.radicand.constant, body.index
                    body_map[key] += body.multiplier
            else:
                body_rest.append(body)

        for key, multiplier in body_map.items():
            if multiplier == 0:
                continue
            rad_const, index = key
            body_rest.append(
                SimpleRadicalElement(
                    multiplier=multiplier,
                    index=index,
                    radicand=SimpleRadical(rad_const)
                )
            )

        return SimpleRadical(constant=const, body=body_rest)

    def _is_integer(self):
        return len(self.body) == 0

    def is_zero(self):
        # TODO: self.body가 normalize되면서 0이 되는 경우는 나중에
        return self.constant == 0 and len(self.body) == 0

    def sqrt(self):
        return SimpleRadical(
            constant=0,
            body=[
                SimpleRadicalElement(multiplier=1, index=2, radicand=self)
            ]
        )

    def to_wolfram_alpha(self):
        stream = []
        if self.constant:
            stream.append(str(self.constant))
        for body in self.body:
            s = body.to_wolfram_alpha()
            if not s.startswith('-') and stream:
                stream.append("+")
            stream.append(s)
        return "".join(stream)


@dataclass(frozen=True, unsafe_hash=True)
class SimpleRadicalElement:
    multiplier: int
    index: int
    radicand: SimpleRadical

    def __neg__(self):
        return SimpleRadicalElement(
            multiplier=-self.multiplier,
            index=self.index,
            radicand=self.radicand
        )

    def __mul__(self, other):
        if isinstance(other, NumberType):
            return SimpleRadicalElement(
                multiplier=self.multiplier * other,
                index=self.index,
                radicand=self.radicand
            )
        assert isinstance(other, SimpleRadicalElement), type(other)  # FIXME: 다른게 오게 될 수도?
        g = math.gcd(self.index, other.index)
        return SimpleRadicalElement(
            multiplier=self.multiplier*other.multiplier,
            index=self.index*other.index//g,
            radicand=(
                (self.radicand ** (other.index//g)) *
                (other.radicand ** (self.index//g))
            )
        )

    def __truediv__(self, other):
        assert isinstance(other, int)
        return SimpleRadicalElement(
            multiplier=self.multiplier // other,
            index=self.index,
            radicand=self.radicand
        )

    def _fast_simplify(self):
        if self.radicand._is_integer():
            power_map = {}
            multiplier = self.multiplier
            index = 1
            for p, e in factorize(self.radicand.constant).items():
                ep, er = divmod(e, self.index)
                multiplier *= pow(p, ep)
                if er > 0:
                    f = power_map[p] = Fraction(er, self.index)
                    index = lcm(index, f.denominator)
            number = 1
            for p, e in power_map.items():
                number *= pow(p, (e*index).numerator)
            return SimpleRadicalElement(
                multiplier=multiplier,
                index=index,
                radicand=SimpleRadical._wrap(number)
            )
        else:
            return self

    def _is_integer(self):
        return self.radicand._is_integer() and self.radicand.constant == 1

    def to_wolfram_alpha(self):
        stream = []
        if self.multiplier != 1:
            stream.append(f"{self.multiplier}*")
        stream.append('sqrt')
        if self.index != 2:
            stream.append(f"[{self.index}]")
        stream.append(f"{{{self.radicand.to_wolfram_alpha()}}}")
        return "".join(stream)
