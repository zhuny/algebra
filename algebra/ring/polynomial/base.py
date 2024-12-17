import collections
import dataclasses
import itertools
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import List

from algebra.field.base import Field, FieldElement
from algebra.ring.base import Ring, RingElement
from algebra.ring.polynomial.monomial_ordering import MonomialOrderingBase, \
    LexicographicMonomialOrdering
from algebra.ring.polynomial.naming import VariableNameGenerator, \
    VariableNameListGenerator, VariableNameIndexGenerator
from algebra.ring.quotient import Ideal, QuotientRing, QuotientRingElement
from algebra.util.decorator import iter_to_str


@dataclass(unsafe_hash=False)
class PolynomialRing(Ring):
    field: Field
    number: int = 1
    naming: 'VariableNameGenerator' = None
    monomial_ordering: MonomialOrderingBase = dataclasses.field(
        default_factory=LexicographicMonomialOrdering
    )

    def __hash__(self) -> int:
        return id(self)

    def __truediv__(self, ideal: 'PolynomialIdeal') -> 'PolynomialQuotientRing':
        super().__truediv__(ideal)  # 타입 확인 용
        return PolynomialQuotientRing(parent=self, ideal=ideal)

    def __post_init__(self):
        # Define and check naming
        if self.naming is None:
            if self.number <= 3:
                self.naming = VariableNameListGenerator('xyz')
            else:
                self.naming = VariableNameIndexGenerator('x')
        if not self.naming.check_range(self.number):
            raise ValueError('Invalid naming range')

    def element(self, coefficient_value):
        coefficient_map = {}
        if isinstance(coefficient_value, dict):
            coefficient_iter = coefficient_value.items()
        elif isinstance(coefficient_value, list):
            coefficient_iter = enumerate(coefficient_value)
        else:
            coefficient_iter = [(0, coefficient_value)]

        for power, coefficient in coefficient_iter:
            power_monomial = self._wrap_monomial(power)
            coefficient_map[power_monomial] = self.field.element(coefficient)

        return PolynomialRingElement(ring=self, value=coefficient_map)

    def zero(self):
        return self.element(0)

    def one(self):
        return self.element(1)

    def variables(self):
        for i in range(self.number):
            power = [0] * self.number
            power[i] = 1
            yield PolynomialRingElement(
                ring=self,
                value={
                    Monomial(power=power, ring=self): self.field.one()
                }
            )

    def _build_ideal(self,
                     element_list: list['PolynomialRingElement']
                     ) -> 'PolynomialIdeal':
        return PolynomialIdeal(ring=self, generator=element_list)

    def _wrap_monomial(self, power: int | list[int]):
        if isinstance(power, int):
            power = [power] + [0] * (self.number - 1)

        if len(power) != self.number:
            raise ValueError("Monomial degree is not matched")

        return Monomial(ring=self, power=power)


@dataclass
class PolynomialRingElement(RingElement):
    ring: PolynomialRing
    value: dict['Monomial', FieldElement]
    _degree: 'Monomial' = None

    def __post_init__(self):
        # drop zero element
        self.value = {
            index: coefficient
            for index, coefficient in self.value.items()
            if not coefficient.is_zero()
        }

        # degree setting
        if self.value:
            self._degree = max(self.value, key=self.ring.monomial_ordering.key)
        else:
            self._degree = self.constant_monomial()

    @iter_to_str
    def __str__(self):
        is_first = True
        abs_one_re = re.compile(r"[+-]?1")

        for monomial, coefficient in self.sorted_term():
            # check sign
            c_str = str(coefficient)
            if not (is_first or c_str.startswith('-')):
                c_str = '+' + c_str

            # check digit
            if abs_one_re.fullmatch(c_str):
                if not monomial.is_constant():
                    c_str = c_str.rstrip('1')

            yield c_str
            yield str(monomial)

            is_first = False

    def __add__(self, other):
        if not isinstance(other, (int, Fraction, PolynomialRingElement)):
            return NotImplemented

        value_map = collections.defaultdict(self.ring.field.zero)

        for pow1, coef1 in itertools.chain(self.value.items(),
                                           self._wrap_iter(other)):
            value_map[pow1] += coef1

        return PolynomialRingElement(ring=self.ring, value=value_map)

    def _wrap_iter(self, other):
        if isinstance(other, (int, Fraction)):
            yield self.constant_monomial(), self.ring.field.element(other)
        elif isinstance(other, PolynomialRingElement):
            yield from other.value.items()

    def __neg__(self):
        return PolynomialRingElement(
            ring=self.ring,
            value={
                k: -v
                for k, v in self.value.items()
            }
        )

    def __mul__(self, other):
        value_map = collections.defaultdict(self.ring.field.zero)

        if isinstance(other, PolynomialRingElement):
            for pow1, coef1 in self.value.items():
                for pow2, coef2 in other.value.items():
                    value_map[pow1 * pow2] += coef1 * coef2
        elif isinstance(other, Monomial):
            for pow1, coef1 in self.value.items():
                value_map[pow1 * other] += coef1
        else:
            for pow1, coef1 in self.value.items():
                value_map[pow1] += coef1 * other

        return PolynomialRingElement(ring=self.ring, value=value_map)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, (int, Fraction)):
            other = self.ring.field.element(other)

        if other.is_zero():
            raise ValueError('Cannot divide by zero')

        return PolynomialRingElement(
            ring=self.ring,
            value={k: v / other for k, v in self.value.items()}
        )

    def __mod__(self, other):
        return self.__divmod__(other)[1]

    def __divmod__(self, other: 'PolynomialRingElement'):
        lm = other.lead_monomial()
        lc = other.lead_coefficient()

        current = self
        result = {}
        while True:
            for monomial, coefficient in current.sorted_term():
                if monomial.is_divisible(lm):
                    coefficient /= lc
                    monomial /= lm
                    result[monomial] = coefficient
                    divisible = PolynomialRingElement(
                        ring=self.ring, value={monomial: coefficient}
                    )
                    current -= divisible * other
                    break
            else:  # if current is not changed, stop iteration.
                break

        return (
            PolynomialRingElement(ring=self.ring, value=result),
            current
        )

    def __getitem__(self, item):
        if item in self.value:
            return self.value[item]
        else:
            return self.ring.element(0)

    def is_zero(self):
        return len(self.value) == 0

    def lead_monomial(self):
        return self._degree

    def lead_coefficient(self):
        if self.value:
            return self.value[self._degree]
        else:
            return self.ring.field.zero()

    def sorted_term(self):
        for monomial in self.sorted_monomial():
            yield monomial, self.value[monomial]

    def sorted_monomial(self):
        return sorted(
            self.value.keys(),
            key=self.ring.monomial_ordering.key,
            reverse=True
        )

    def constant_monomial(self):
        return Monomial(ring=self.ring, power=[0]*self.ring.number)

    def s_polynomial(self, e2: 'PolynomialRingElement'
                     ) -> 'PolynomialRingElement':
        if self.is_zero() or e2.is_zero():
            return self.ring.element([])

        self_mono = self.lead_monomial()
        self_c = self.lead_coefficient()
        e2_mono = e2.lead_monomial()
        e2_c = e2.lead_coefficient()

        e3 = self_mono.gcd(e2_mono)

        return (
                (e2_mono / e3) * self / self_c -
                (self_mono / e3) * e2 / e2_c
        )


@dataclass
class Monomial:
    power: List[int]
    ring: 'PolynomialRing'

    def __post_init__(self):
        for i, p in enumerate(self.power):
            if p < 0:
                raise ValueError(f"{i}-th index is negative.")

    @iter_to_str
    def __str__(self):
        for index, power in enumerate(self.power):
            if power == 0:
                continue
            yield self.ring.naming.get(index)
            if power > 1:
                yield f'^{power}'

    def __hash__(self):
        return hash((tuple(self.power), self.ring))

    def __mul__(self, other):
        if isinstance(other, Monomial):
            if self.ring != other.ring:
                raise ValueError("Operation can be with same ring")

            power = [x + y for x, y in zip(self.power, other.power)]
            return Monomial(power=power, ring=self.ring)

        return NotImplemented

    def __truediv__(self, other):
        if not self.is_divisible(other):
            raise ValueError("Cannot Divisible")
        if self.ring != other.ring:
            raise ValueError("Operation can be with same ring")

        power = [x - y for x, y in zip(self.power, other.power)]
        return Monomial(power=power, ring=self.ring)

    def is_constant(self):
        for power in self.power:
            if power > 0:
                return False
        return True

    def is_divisible(self, other: 'Monomial'):
        if self.ring != other.ring:
            raise ValueError("Operation can be with same ring")

        for x, y in zip(self.power, other.power):
            if x < y:
                return False
        return True

    def gcd(self, other: 'Monomial') -> 'Monomial':
        return Monomial(
            power=[min(x, y) for x, y in zip(self.power, other.power)],
            ring=self.ring
        )

    def lcm(self, other: 'Monomial') -> 'Monomial':
        return Monomial(
            power=[max(x, y) for x, y in zip(self.power, other.power)],
            ring=self.ring
        )


@dataclass
class PolynomialIdeal(Ideal):
    generator: list[PolynomialRingElement]

    def is_contained(self, element):
        for generator in self.generator:
            element %= generator
        return element.is_zero()


@dataclass
class PolynomialQuotientRing(QuotientRing):
    parent: PolynomialRing
    ideal: PolynomialIdeal

    def element(self, *args):
        parent = super().element(*args)
        return PolynomialQuotientRingElement(ring=self, element=parent.element)


@dataclass(eq=False)
class PolynomialQuotientRingElement(QuotientRingElement):
    ring: PolynomialQuotientRing
    element: PolynomialRingElement

    def minimal_polynomial(self):
        from algebra.ring.polynomial.buchberger import BuchbergerAlgorithm

        ba = BuchbergerAlgorithm(self.ring.ideal.generator)
        ba.run()
        return ba.minimal_polynomial(self.element)
