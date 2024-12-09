import collections
import itertools
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Union

from algebra.number.base import RingBase, CalculationStep
from algebra.number.types import NumberType, Number
from algebra.number.util import factorize
from algebra.polynomial.polynomial import Polynomial


def remove_zero(dict_value: dict):
    return {
        k: v
        for k, v in dict_value.items()
        if v != 0
    }


class ElementMerger:
    def __init__(self):
        self.multiply = collections.defaultdict(int)
        self.power = {}

    def update(self, term):
        self.multiply[term.key] += term.multiply
        self.power[term.key] = term.power

    def to_radical(self):
        result = []
        for term_key, term_power in self.power.items():
            multiply = self.multiply[term_key]
            if multiply != 0:
                result.append(
                    ODRadicalElement(
                        multiply=multiply,
                        power=term_power
                    )
                )
        return ODRadical(body=result)


@dataclass(eq=False)
class ODRadical(RingBase):
    body: list['ODRadicalElement']

    @classmethod
    def from_number(cls, number, root=2, multiply=1):
        child = ODRadicalElement.from_number(number, root, multiply)
        return cls(body=[child])

    def __str__(self):
        return ''.join(str(child) for child in self.body)

    def __add__(self, other):
        if isinstance(other, ODRadical):
            other_iter = other.body
        elif isinstance(other, Number):
            other_iter = [ODRadicalElement.wrap_number(other)]
        else:
            raise TypeError("Unknown Type")

        merger = ElementMerger()
        for rad in itertools.chain(self.body, other_iter):
            merger.update(rad)

        return merger.to_radical()

    def __neg__(self):
        return ODRadical([-element for element in self.body])

    def __mul__(self, other):
        if isinstance(other, NumberType):
            return ODRadical([
                element * other
                for element in self.body
            ])
        elif isinstance(other, ODRadical):
            merger = ElementMerger()
            for b1 in self.body:
                for b2 in other.body:
                    merger.update(b1 * b2)

            return merger.to_radical()
        else:
            raise TypeError("Unknown Type")

    def __truediv__(self, other):
        upper = self
        lower: ODRadical = other

        while True:
            if lower.is_integer():
                return upper * (1 / lower.get_integer())

            left, right, key = lower._split(False)
            mul = left - right
            upper *= mul
            lower *= mul

    def is_zero(self):
        return len(self.body) == 0

    def get(self, key):
        for element in self.body:
            if element.key == key:
                return element.multiply
        return 0

    def min_key(self):
        return min(self.key_list())

    def minimum_polynomial(self):
        rrp = RowReducePolynomial(self)
        return rrp.reduce()

    def key_list(self):
        for element in self.body:
            yield element.key

    def is_integer(self):
        if len(self.body) > 1:
            return False

        for element in self.body:
            if element.key == ():
                return True
            else:
                return False

        return True

    def get_integer(self):
        assert self.is_integer()
        for element in self.body:
            return element.multiply

    def _split(self, pop=True):
        key = self._get_any_root()
        left = ODRadical([])
        right = ODRadical([])

        for body in self.body:
            if key in body.power:
                if pop:
                    body = body.pop(key)
                right.body.append(body)
            else:
                left.body.append(body)

        return left, right, key

    def _get_any_root(self):
        for element in self.body:
            for key in element.power:
                if key > 1:
                    return key

        raise ValueError("Maybe Integer")

    def _is_all_positive(self):
        for element in self.body:
            if element.multiply < 0:
                return False
        return True

    def _is_all_negative(self):
        for element in self.body:
            if element.multiply > 0:
                return False
        return True

    def is_positive(self):
        current = self

        while True:
            if current._is_all_positive():
                return True
            elif current._is_all_negative():
                return False

            left, right, key = current._split()

            left_positive = left.is_positive()
            right_positive = right.is_positive()

            if left_positive and right_positive:
                return True
            if not (left_positive or right_positive):
                return False

            d = left * left - right * right * key
            if left_positive:
                current = d
            else:
                current = -d

    def __ceil__(self):
        if self.is_integer():
            return self.get_integer()

        if self.is_positive():
            start = 0
            end = None
        else:
            start = None
            end = 0

        bs = BinarySearch(start, end)
        while bs.is_long():
            mid = bs.get_middle()
            if (self - mid).is_positive():
                bs.set_start(mid)
            else:
                bs.set_end(mid)

        return bs.start


class ProgrammingError(Exception):
    pass


class BinarySearch:
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

        self.search_limit = 100

    def set_start(self, start):
        self.start = start

    def set_end(self, end):
        self.end = end

    def is_long(self) -> bool:
        return (
            self.start is None or
            self.end is None or
            self.end - self.start > 1
        )

    def get_middle(self):
        if self.start is None:
            if self.end == 0:
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


@dataclass
class ODRadicalElement:
    multiply: NumberType
    power: dict[int: Fraction]
    key_: Any = None

    @classmethod
    def from_number(cls, number, root=2, multiply=1):
        power_dict = {}

        for k, v in factorize(number).items():
            if v >= root:
                multiply *= pow(k, v // root)
                v %= root

            power_dict[k] = Fraction(1, root)

        return cls(
            multiply=Fraction(multiply),
            power=power_dict
        )

    @classmethod
    def wrap_number(cls, number):
        return cls(multiply=number, power={})

    def pop(self, key):
        power = dict(self.power)
        power.pop(key, None)
        return ODRadicalElement(self.multiply, power)

    def __str__(self):
        sign = '+' if self.multiply > 0 else '-'
        return f'{sign}{abs(self.multiply)}*{self.power}'

    def __hash__(self):
        return hash(self.key_)

    def __neg__(self):
        return ODRadicalElement(
            multiply=-self.multiply,
            power=self.power,
            key_=self.key
        )

    def __mul__(self, other: Union[Number, 'ODRadicalElement']):
        if isinstance(other, NumberType):
            return ODRadicalElement(
                multiply=self.multiply * other,
                power=self.power,
                key_=self.key
            )
        elif isinstance(other, ODRadicalElement):
            power_dict = collections.defaultdict(Fraction)
            for p, e in itertools.chain(self.power.items(),
                                        other.power.items()):
                power_dict[p] += e

            multiply = self.multiply * other.multiply
            for p, e in power_dict.items():
                if 1 <= e:
                    multiply *= pow(p, int(e))
                    power_dict[p] = e % 1

            return ODRadicalElement(
                multiply=multiply,
                power=remove_zero(power_dict)
            )
        else:
            raise TypeError("Unknown Type")

    @property
    def key(self):
        if self.key_ is None:
            self.key_ = self._get_key()
        return self.key_

    def _get_key(self):
        return tuple(sorted(self.power.items()))


class RowReducePolynomial:
    def __init__(self, number):
        self.body: list[Row] = []
        self.number = number

    def append(self, number: ODRadical):
        self.body.append(Row(len(self.body), number))

    def reduce_iter(self):
        yield CalculationStep(
            name="Add",
            argv=[self.append(self.number.from_number(1, 1))]
        )

        current = self.number
        degree = set()
        for i in itertools.count(1):
            yield CalculationStep(
                name="Add",
                argv=[self.append(current)]
            )
            degree.update(current.key_list())
            current *= self.number

            if len(degree) == i:
                break

        for row1, row2 in itertools.combinations(self.body, 2):
            key = row1.number.min_key()
            num1 = row1.number.get(key)
            num2 = row2.number.get(key)
            if num2 == 0:
                continue

            row2.sub(row1, num2 / num1)
            yield CalculationStep(
                name="Sub",
                argv=[row1, row2]
            )

    def reduce(self):
        for _ in self.reduce_iter():
            pass
        return self.body[-1].polynomial


class Row:
    def __init__(self, degree, number):
        self.polynomial = Polynomial({degree: 1})
        self.number = number

    def sub(self, row: 'Row', number):
        self.polynomial -= row.polynomial * number
        self.number -= row.number * number
