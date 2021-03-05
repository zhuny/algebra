import collections
from fractions import Fraction
from typing import List, Dict, Union

from algebra.number.types import NumberType


class Polynomial:
    def __init__(self, body: Union[List[Fraction], Dict[int, Fraction]]):
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

    def __eq__(self, other):
        return isinstance(other, Polynomial) and self.body == other.body
