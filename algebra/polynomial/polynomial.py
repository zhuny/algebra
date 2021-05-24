import collections
import functools
import itertools
import math
from dataclasses import dataclass
from fractions import Fraction
from operator import itemgetter
from typing import List, Dict, Union

from algebra.matrix.matrix import Matrix
from algebra.number.types import NumberType, Number
from algebra.number.util import lcm, divisor_function, divisor_list


@dataclass(init=False)
class Polynomial:
    body: Dict[int, Number]
    degree: int

    def __init__(self, body: Union[List[Number], Dict[int, Number]]):
        if isinstance(body, list):
            body = dict(enumerate(body))
        assert isinstance(body, dict)

        self.body = {k: Fraction(v) for k, v in body.items() if v != 0}
        self.degree = max(self.body, default=0)

    @classmethod
    def from_map(cls, key_value: Dict[int, Number]):
        n = len(key_value)
        m = Matrix(n, n)
        row = []
        for i, x in enumerate(key_value):
            xp = Fraction(1)
            for j in range(n):
                m[i, j] = xp
                xp *= x
            row.append(key_value[x])
        m.reduced_form(row)
        return cls(row)

    def __add__(self, other):
        assert isinstance(other, Polynomial)
        d = collections.defaultdict(Fraction)
        for i, num in self.body.items():
            d[i] += num
        for i, num in other.body.items():
            d[i] += num
        return Polynomial(d)

    def __sub__(self, other):
        assert isinstance(other, Polynomial)
        d = collections.defaultdict(Fraction)
        for i, num in self.body.items():
            d[i] += num
        for i, num in other.body.items():
            d[i] -= num
        return Polynomial(d)

    def __mul__(self, other):
        if isinstance(other, NumberType):
            other_body = {0: Fraction(other)}
        elif isinstance(other, Polynomial):
            other_body = other.body
        else:
            raise ValueError("Should be NumberType or Polynomial")

        d = collections.defaultdict(Fraction)
        for i, num1 in self.body.items():
            for j, num2 in other_body.items():
                d[i + j] += num1 * num2
        return Polynomial(d)

    def __truediv__(self, other):
        if isinstance(other, NumberType):
            return Polynomial({k: v / other for k, v in self.body.items()})

        raise ValueError(f"Cannot divided by {other!r}")

    def __divmod__(self, other):
        current = self
        q = Polynomial({})

        if other.degree == 0:
            return self / other[0], q

        while current.degree >= other.degree:
            diff = current.degree-other.degree
            p = Polynomial({
                diff: current[current.degree] / other[other.degree]
            })
            q += p
            current -= p * other
        assert q * other + current == self
        return q, current

    def __neg__(self):
        return Polynomial({k: -v for k, v in self.body.items()})

    def __eq__(self, other):
        if isinstance(other, NumberType):
            other = Polynomial([other])
        return isinstance(other, Polynomial) and self.body == other.body

    def __getitem__(self, item):
        return self.body.get(item, Fraction())

    def __call__(self, x):
        degree = max(self.body, default=Fraction())
        value = self[degree]
        while degree > 0:
            degree -= 1
            value = value * x + self[degree]
        return value

    def to_integer_coefficient(self):
        deno = functools.reduce(lcm, [coeff.denominator for coeff in self.body.values()])
        return self * deno

    def is_integer_coefficient(self):
        for coeff in self.body.values():
            if coeff.denominator != 1:
                return False
        return True

    def to_wolfram_alpha(self):
        stream = []
        for p, coeff in sorted(self.body.items(), reverse=True):
            if stream and coeff > 0:
                stream.append("+")
            if coeff != 1 or p == 0:
                stream.append(f"{coeff}")
            if p > 1:
                stream.append(f"x**{p}")
            elif p == 1:
                stream.append("x")
        return "".join(stream)

    def diff(self):
        d = {}
        for k, v in self.body.items():
            if k > 0:
                d[k - 1] = v * k
        return Polynomial(d)

    def _value(self, i):
        v = self(i)
        return i, v, divisor_function(abs(v))*2 if v != 0 else 1

    def _num_factor(self, n):
        if n == 0:
            return [0]
        else:
            factor_list = list(divisor_list(abs(n)))
            factor_list.extend([-d for d in factor_list])
            return factor_list

    def _check_this_value(self, v1, v2):
        if v2 == 0:
            return v1 == 0
        else:
            return v1 % v2 == 0

    def factorize(self) -> List['Polynomial']:
        if self.degree < 2:
            return [self]

        degree = max(self.body, default=0)
        many = degree // 2

        value = [
            (
                i,
                (v := int(self(i))),
                divisor_function(abs(v))*2 if v != 0 else 1
            )
            for i in range(-100, 100)
        ]
        value.sort(key=itemgetter(2, 1, 0))
        picked = value[:many]
        picked_factor = [self._num_factor(v[1]) for v in picked]
        checker = value[many]

        for each_value in itertools.product(*picked_factor):
            poly: Polynomial = Polynomial.from_map({
                x[0]: z
                for x, z in zip(picked, each_value)
            })
            if poly.degree > 0 and poly.is_integer_coefficient():
                if poly[poly.degree] < 0:
                    poly = -poly
                if self._check_this_value(checker[1], poly(checker[0])):
                    q, r = divmod(self, poly)
                    if r == 0:
                        return poly.factorize() + q.factorize()

        return [self]
