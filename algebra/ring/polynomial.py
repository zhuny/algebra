import collections
import itertools
from dataclasses import dataclass

from algebra.field.base import Field, FieldElement
from algebra.ring.base import Ring, RingElement
from algebra.ring.quotient import Ideal


@dataclass
class PolynomialRing(Ring):
    field: Field
    number: int = 1

    def element(self, coefficient_list):
        coefficient_map = {}
        for power, coefficient in enumerate(coefficient_list):
            coefficient_map[power] = self.field.element(coefficient)

        return PolynomialRingElement(ring=self, value=coefficient_map)

    def _build_ideal(self,
                     element_list: list['PolynomialRingElement']
                     ) -> 'PolynomialIdeal':
        return PolynomialIdeal(ring=self, generator=element_list)


@dataclass
class PolynomialRingElement(RingElement):
    ring: PolynomialRing
    value: dict[int, FieldElement]
    degree: int = 0

    def __post_init__(self):
        # drop zero element
        for index, coefficient in list(self.value.items()):
            if coefficient == 0:
                self.value.pop(index)

        # degree setting
        if self.value:
            self.degree = max(self.value)
        else:
            self.degree = -1

    def __add__(self, other):
        value_map = collections.defaultdict(self.ring.field.zero)

        for pow1, coef1 in itertools.chain(self.value.items(),
                                           other.value.items()):
            value_map[pow1] += coef1

        return PolynomialRingElement(ring=self.ring, value=value_map)

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
                    value_map[pow1 + pow2] += coef1 * coef2
        else:
            for pow1, coef1 in self.value.items():
                value_map[pow1] += coef1 * other

        return PolynomialRingElement(ring=self.ring, value=value_map)

    def __rmul__(self, other):
        return self * other

    def __mod__(self, other: 'PolynomialRingElement'):
        current = self
        while current.degree >= other.degree:
            offset_degree = current.degree - other.degree
            offset = current.lead_coefficient() / other.lead_coefficient()
            offset_poly = PolynomialRingElement(
                ring=current.ring,
                value={offset_degree: offset}
            )
            current -= offset_poly * other

        return current

    def is_zero(self):
        return len(self.value) == 0

    def lead_coefficient(self):
        return self.value[self.degree]


@dataclass
class PolynomialIdeal(Ideal):
    def is_contained(self, element):
        for generator in self.generator:
            element %= generator
        return element.is_zero()
