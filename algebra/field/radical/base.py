import collections
import functools
import itertools
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Union

from algebra.field.rational import RationalField, RationalFieldElement
from algebra.number.base import RingBase, CalculationStep
from algebra.number.types import Number, NumberType
from algebra.number.util import factorize
from algebra.polynomial.polynomial import Polynomial
from algebra.ring.polynomial.base import PolynomialRingElement, PolynomialRing, \
    PolynomialIdeal
from algebra.ring.polynomial.monomial_ordering import \
    GradedReverseLexicographicOrdering
from algebra.util.decorator import iter_to_str


@dataclass
class Interval:
    start: NumberType
    end: NumberType

    def __post_init__(self):
        if not isinstance(self.start, Fraction):
            self.start = Fraction(self.start)
        if not isinstance(self.end, Fraction):
            self.end = Fraction(self.end)

    def __add__(self, other):
        return Interval(
            start=Fraction(self.start + other.start),
            end=Fraction(self.end + other.end)
        )

    def __sub__(self, other):
        return Interval(
            start=Fraction(self.start - other.start),
            end=Fraction(self.end - other.end)
        )

    def __mul__(self, other):
        if isinstance(other, Interval):
            valid_values = [
                self.start * other.start, self.start * other.end,
                self.end * other.start, self.end * other.end
            ]
        else:
            valid_values = [self.start * other, self.end * other]

        return Interval(
            start=min(valid_values),
            end=max(valid_values)
        )

    def __truediv__(self, other):
        if other.start <= 0 <= other.end:
            raise ValueError("Not divisible by zero")

        valid_values = [
            self.start / other.start, self.start / other.end,
            self.end / other.start, self.end / other.end
        ]
        return Interval(
            start=min(valid_values),
            end=max(valid_values)
        )

    @property
    def middle(self):
        return (self.start + self.end) / 2

    def same_floor(self):
        start = math.floor(self.start)
        end = math.floor(self.end)
        return start == end

    def floor(self):
        return math.floor(self.start)


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
class ODRadical:
    body: dict['ODRadicalElement', Fraction]
    interval: Interval = None

    @classmethod
    def sqrt(cls, number, root=2):
        power = {}
        mult = 1
        for p, e in factorize(number).items():
            p_over, p_re = divmod(Fraction(e) / root, 1)
            if p_over > 0:
                mult *= pow(p, p_over)
            if p_re > 0:
                power[p] = p_re

        element = ODRadicalElement(power=power)
        return cls(body={element: Fraction(mult)})

    def __post_init__(self):
        self.interval_refresh()

    def __add__(self, other):
        d = collections.defaultdict(Fraction)

        if isinstance(other, (int, Fraction)):
            d[ODRadicalElement.one()] += other
        elif isinstance(other, RationalFieldElement):
            d[ODRadicalElement.one()] += other.value
        elif isinstance(other, ODRadical):
            for k, v in other.body.items():
                d[k] += v
        else:
            return NotImplemented

        for k, v in self.body.items():
            d[k] += v

        return ODRadical(body=remove_zero(d))

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if isinstance(other, (int, Fraction)):
            return self._mul_const(other)
        elif isinstance(other, RationalFieldElement):
            return self._mul_const(other.value)
        elif isinstance(other, ODRadical):
            d = collections.defaultdict(Fraction)
            for k1, v1 in self.body.items():
                for k2, v2 in other.body.items():
                    k3, v3 = k1.multiple(k2)
                    d[k3] += v1 * v2 * v3
            return ODRadical(body=remove_zero(d))
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, RationalFieldElement):
            return self._mul_const(1 / other.value)
        else:
            return NotImplemented

    def __pow__(self, power):
        if power == 0:
            return 1
        elif power == 1:
            return self

        current = self
        for i in range(1, power):
            current *= self
        return current

    def __floor__(self):
        while not self.interval.same_floor():
            self.interval_update()
        return self.interval.floor()

    @iter_to_str
    def __str__(self):
        items = [
            (element.key, element, multiplier)
            for element, multiplier in self.body.items()
        ]
        items.sort()
        for key, element, multiplier in items:
            if multiplier > 0:
                yield "+"
            yield str(multiplier)
            yield "*"
            yield str(element)

    def interval_update(self):
        for child in self.body:
            child.interval_update()
        self.interval_refresh()

    def interval_refresh(self):
        i = Interval(0, 0)
        for child, multiplier in self.body.items():
            i += child.interval * multiplier
        self.interval = i

    def inv(self):
        mp = self.minimal_polynomial
        x = mp.ring.element([0, 1])
        inv_p, constant = divmod(mp, x)

        return inv_p([self]) / (-constant[0])

    @functools.cached_property
    def minimal_polynomial(self) -> PolynomialRingElement:
        return MinimalPolynomialCalculator(self).run()

    def _mul_const(self, other):
        return ODRadical(body={
            k: v * other
            for k, v in self.body.items()
        })

    # def __neg__(self):
    #     return ODRadical([-element for element in self.body])
    #
    # def __mul__(self, other):
    #     if isinstance(other, NumberType):
    #         return ODRadical([
    #             element * other
    #             for element in self.body
    #         ])
    #     elif isinstance(other, ODRadical):
    #         merger = ElementMerger()
    #         for b1 in self.body:
    #             for b2 in other.body:
    #                 merger.update(b1 * b2)
    #
    #         return merger.to_radical()
    #     else:
    #         raise TypeError("Unknown Type")
    #
    # def __truediv__(self, other):
    #     upper = self
    #     lower: ODRadical = other
    #
    #     while True:
    #         if lower.is_integer():
    #             return upper * (1 / lower.get_integer())
    #
    #         left, right, key = lower._split(False)
    #         mul = left - right
    #         upper *= mul
    #         lower *= mul
    #
    # def is_zero(self):
    #     return len(self.body) == 0
    #
    # def get(self, key):
    #     for element in self.body:
    #         if element.key == key:
    #             return element.multiply
    #     return 0
    #
    # def min_key(self):
    #     return min(self.key_list())
    #
    # def minimum_polynomial(self):
    #     rrp = RowReducePolynomial(self)
    #     return rrp.reduce()
    #
    # def key_list(self):
    #     for element in self.body:
    #         yield element.key
    #
    # def is_integer(self):
    #     if len(self.body) > 1:
    #         return False
    #
    #     for element in self.body:
    #         if element.key == ():
    #             return True
    #         else:
    #             return False
    #
    #     return True
    #
    # def get_integer(self):
    #     assert self.is_integer()
    #     for element in self.body:
    #         return element.multiply
    #
    # def _split(self, pop=True):
    #     key = self._get_any_root()
    #     left = ODRadical([])
    #     right = ODRadical([])
    #
    #     for body in self.body:
    #         if key in body.power:
    #             if pop:
    #                 body = body.pop(key)
    #             right.body.append(body)
    #         else:
    #             left.body.append(body)
    #
    #     return left, right, key
    #
    # def _get_any_root(self):
    #     for element in self.body:
    #         for key in element.power:
    #             if key > 1:
    #                 return key
    #
    #     raise ValueError("Maybe Integer")
    #
    # def _is_all_positive(self):
    #     for element in self.body:
    #         if element.multiply < 0:
    #             return False
    #     return True
    #
    # def _is_all_negative(self):
    #     for element in self.body:
    #         if element.multiply > 0:
    #             return False
    #     return True
    #
    # def is_positive(self):
    #     current = self
    #
    #     while True:
    #         if current._is_all_positive():
    #             return True
    #         elif current._is_all_negative():
    #             return False
    #
    #         left, right, key = current._split()
    #
    #         left_positive = left.is_positive()
    #         right_positive = right.is_positive()
    #
    #         if left_positive and right_positive:
    #             return True
    #         if not (left_positive or right_positive):
    #             return False
    #
    #         d = left * left - right * right * key
    #         if left_positive:
    #             current = d
    #         else:
    #             current = -d
    #
    # def __ceil__(self):
    #     if self.is_integer():
    #         return self.get_integer()
    #
    #     if self.is_positive():
    #         start = 0
    #         end = None
    #     else:
    #         start = None
    #         end = 0
    #
    #     bs = BinarySearch(start, end)
    #     while bs.is_long():
    #         mid = bs.get_middle()
    #         if (self - mid).is_positive():
    #             bs.set_start(mid)
    #         else:
    #             bs.set_end(mid)
    #
    #     return bs.start


@dataclass(unsafe_hash=False, eq=False)
class ODRadicalElement:
    power: dict[int, Fraction]
    interval: Interval = None
    _key = None

    @classmethod
    def one(cls):
        return cls(power={})

    def __post_init__(self):
        end = 1
        for p in self.power:
            end *= p
        self.interval = Interval(1, end)

    @iter_to_str
    def __str__(self):
        for k, v in sorted(self.power.items()):
            yield f"{k}({v})"

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other.key

    def multiple(self, other: 'ODRadicalElement'):
        power_d = collections.defaultdict(Fraction)

        for p, e in itertools.chain(self.power.items(), other.power.items()):
            power_d[p] += e

        result = {}
        multiplier = 1
        for p, e in power_d.items():
            while e >= 1:
                multiplier *= p
                e -= 1
            if e > 0:
                result[p] = e
        return ODRadicalElement(power=result), multiplier

    def interval_update(self):
        middle = self.interval.middle
        denominator_lcm = self.denominator_lcm()

        left = middle ** denominator_lcm
        right = 1
        for p, e in self.power.items():
            right *= pow(p, int(e * denominator_lcm))
        if left <= right:
            self.interval.start = middle
        else:
            self.interval.end = middle

    @property
    def key(self):
        if self._key is None:
            self._key = tuple(sorted(self.power.items()))
        return self._key

    def denominator_lcm(self):
        answer = 1
        for e in self.power.values():
            answer = math.lcm(answer, e.denominator)
        return answer

    # def pop(self, key):
    #     power = dict(self.power)
    #     power.pop(key, None)
    #     return ODRadicalElement(self.multiply, power)
    #
    # def __str__(self):
    #     sign = '+' if self.multiply > 0 else '-'
    #     return f'{sign}{abs(self.multiply)}*{self.power}'
    #
    #
    # def __neg__(self):
    #     return ODRadicalElement(
    #         multiply=-self.multiply,
    #         power=self.power,
    #         key_=self.key
    #     )
    #
    # def __mul__(self, other: Union[Number, 'ODRadicalElement']):
    #     if isinstance(other, NumberType):
    #         return ODRadicalElement(
    #             multiply=self.multiply * other,
    #             power=self.power,
    #             key_=self.key
    #         )
    #     elif isinstance(other, ODRadicalElement):
    #         power_dict = collections.defaultdict(Fraction)
    #         for p, e in itertools.chain(self.power.items(),
    #                                     other.power.items()):
    #             power_dict[p] += e
    #
    #         multiply = self.multiply * other.multiply
    #         for p, e in power_dict.items():
    #             if 1 <= e:
    #                 multiply *= pow(p, int(e))
    #                 power_dict[p] = e % 1
    #
    #         return ODRadicalElement(
    #             multiply=multiply,
    #             power=remove_zero(power_dict)
    #         )
    #     else:
    #         raise TypeError("Unknown Type")
    #
    # def _interval_update(self):
    #     middle = self._interval.middle / self.multiply
    #
    # def _denominator_lcm(self):
    #     result = 1
    #     for power in self.power.values():
    #         result = math.lcm(result, power.denominator)
    #     return result


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


class MinimalPolynomialCalculator:
    def __init__(self, value: ODRadical):
        self.value = value

    def run(self):
        n = self.needed_variables()
        ring = PolynomialRing(
            field=RationalField(),
            number=n,
            monomial_ordering=GradedReverseLexicographicOrdering()
        )
        ring_variables = ring.variables()
        generators = []
        element_variable = ring.zero()

        for element, multiplier in self.value.body.items():
            v, g = self.get_min_polynomial(element, ring_variables)
            generators.extend(g)
            element_variable += multiplier * v

        last_variable = next(ring_variables)
        generators.append(element_variable - last_variable)

        quotient = ring / ring.ideal(generators)
        self_ = quotient.element(last_variable)
        return self_.minimal_polynomial()

    def needed_variables(self):
        answer = 1
        for element in self.value.body.keys():
            answer += len(element.power)
        return answer

    def get_min_polynomial(self, element: ODRadicalElement, ring_variables):
        variable = 1
        g_list = []

        for p, e in element.power.items():
            x = next(ring_variables)
            variable *= x
            g_list.append(x ** e.denominator - p ** e.numerator)

        return variable, g_list
