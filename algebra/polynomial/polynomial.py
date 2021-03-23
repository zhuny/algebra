import collections
from fractions import Fraction
from typing import List, Dict, Union

from algebra.number.types import NumberType, Number


class Polynomial:
    def __init__(self, body: Union[List[Number], Dict[int, Number]]):
        if isinstance(body, list):
            body = dict(enumerate(body))
        assert isinstance(body, dict)

        self.body = {k: Fraction(v) for k, v in body.items() if v != 0}

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
                d[i+j] += num1 * num2
        return Polynomial(d)

    def __truediv__(self, other):
        if isinstance(other, NumberType):
            return Polynomial({k: v/other for k, v in self.body.items()})

        raise ValueError("Cannot divided")

    def __eq__(self, other):
        return isinstance(other, Polynomial) and self.body == other.body

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
                d[k-1] = v*k
        return Polynomial(d)
