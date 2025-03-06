import collections
import copy
import functools
import itertools
import math
import re
import warnings
from fractions import Fraction
from functools import singledispatchmethod
from typing import List

from pydantic import BaseModel

from algebra.field.base import Field, FieldElement
from algebra.matrix.matrix import Matrix
from algebra.ring.base import Ring, RingElement
from algebra.ring.polynomial.monomial_ordering import MonomialOrderingBase
from algebra.ring.polynomial.naming import VariableNameGenerator
from algebra.ring.polynomial.variable import VariableSystemBase, VariableSystem, \
    VariableContainer
from algebra.ring.quotient import Ideal, QuotientRing, QuotientRingElement
from algebra.util.decorator import iter_to_str
from algebra.util.zero_dict import remove_zero_dict


class PolynomialRing(Ring):
    field: Field
    number: int = 0
    variable_system: (
            VariableSystemBase | VariableNameGenerator
    ) = None

    def model_post_init(self, __context):
        # number와 variable_system 값 구죽하기 시작
        number = self.number
        variable_system = None
        variable_name = None
        monomial_order = None

        if self.variable_system is not None:
            if isinstance(self.variable_system, VariableSystemBase):
                variable_system = self.variable_system
                monomial_order = variable_name = variable_system
            elif isinstance(self.variable_system, VariableNameGenerator):
                variable_name = self.variable_system
            elif isinstance(self.variable_system, MonomialOrderingBase):
                monomial_order = self.variable_system

        if variable_name is None:
            if number == 0:
                raise ValueError("Number or variable name must be specified")
            variable_name = number  # VariableSystem에서 wrapping 해줌

        if variable_system is None:
            # combine 등의 고급 기능을 쓰려면 이렇게 값이 비우지 않았을 것이다.
            variable_system = VariableSystem(
                naming=variable_name,
                ordering=monomial_order  # none 일 경우 자동 지정
            )

        if number == 0:
            number = variable_system.get_size()
        elif self.number != variable_system.get_size():
            raise ValueError("Number and variable system must be equal size")

        self.number = number
        self.variable_system = variable_system

        # variable construction

    @functools.cached_property
    def variable(self) -> VariableContainer:
        # run only once
        container = VariableContainer()
        self.variable_system.register_variable(container, self._variable_list())
        return container

    def __hash__(self) -> int:
        return id(self)

    def __truediv__(self, ideal: 'PolynomialIdeal') -> 'PolynomialQuotientRing':
        super().__truediv__(ideal)  # 타입 확인 용
        return PolynomialQuotientRing(parent=self, ideal=ideal)

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
        warnings.warn("Use ring.variable")
        return self.variable

    def _variable_list(self):
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
        if isinstance(power, Monomial):
            return power

        if isinstance(power, int):
            power = [power] + [0] * (self.number - 1)

        if len(power) != self.number:
            raise ValueError("Monomial degree is not matched")

        return Monomial(ring=self, power=power)


class PolynomialRingElement(RingElement):
    ring: PolynomialRing
    value: dict['Monomial', FieldElement]
    _degree: 'Monomial' = None

    def model_post_init(self, __context):
        # drop zero element
        self.value = remove_zero_dict(self.value)

        # degree setting
        if self.value:
            self._degree = max(self.value, key=self.monomial_key)
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

        # 아무것도 없는 경우
        if is_first:
            yield '0'

    def __add__(self, other):
        if isinstance(other, FieldElement):
            if other.field != self.ring.field:
                return ValueError("Field not matched")

        elif not isinstance(other, (int, Fraction, PolynomialRingElement)):
            return NotImplemented

        value_map = collections.defaultdict(self.ring.field.zero)

        for pow1, coef1 in itertools.chain(self.value.items(),
                                           self._wrap_iter(other)):
            value_map[pow1] += coef1

        return PolynomialRingElement(ring=self.ring, value=value_map)

    def __radd__(self, other):
        return self + other

    def _wrap_iter(self, other):
        if isinstance(other, (int, Fraction)):
            yield self.constant_monomial(), self.ring.field.element(other)
        elif isinstance(other, PolynomialRingElement):
            yield from other.value.items()
        elif isinstance(other, FieldElement):
            if self.ring.field == other.field:
                yield self.constant_monomial(), other

    def __rsub__(self, other):
        return other + (-self)

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

    @singledispatchmethod
    def __truediv__(self, other):
        if not isinstance(other, PolynomialRingElement):
            return NotImplemented

        return divmod(self, other)[0]

    @__truediv__.register
    def _(self, other: int | Fraction | FieldElement):
        if isinstance(other, (int, Fraction)):
            other = self.ring.field.element(other)

        if other.is_zero():
            raise ValueError('Cannot divide by zero')

        return PolynomialRingElement(
            ring=self.ring,
            value={k: v / other for k, v in self.value.items()}
        )

    def __pow__(self, power: int, modulo=None) -> 'PolynomialRingElement':
        if not (isinstance(power, int) and power > 0):
            return NotImplemented

        pow_result = 1
        current = self
        while power > 0:
            if power % 2 == 1:
                pow_result *= current
                if modulo:
                    pow_result %= modulo

            current *= current
            if modulo:
                current %= modulo

            power //= 2

        return pow_result

    def __mod__(self, other):
        if not isinstance(other, PolynomialRingElement):
            return NotImplemented

        return divmod(self, other)[1]

    def __divmod__(self, other: 'PolynomialRingElement'):
        if not isinstance(other, PolynomialRingElement):
            return NotImplemented

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
        item = self.ring._wrap_monomial(item)

        if item in self.value:
            return self.value[item]
        else:
            return self.ring.field.element(0)

    def __call__(self, value_list):
        answer = 0
        for monomial, coefficient in self.value.items():
            answer += monomial(value_list) * coefficient
        return answer

    def __eq__(self, other):
        return (self - other).is_zero()

    def __ne__(self, other):
        return not (self == other)

    def is_zero(self):
        return len(self.value) == 0

    def is_one(self):
        return (self - 1).is_zero()

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
            reverse=True, key=self.monomial_key
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

    def monic(self):
        return self / self.lead_coefficient()

    def to_integer(self):
        assert self.ring.field.get_char() == 0

        answer = 1
        for c in self.value.values():
            v: Fraction = c.value
            answer = math.lcm(answer, v.denominator)
        return self * answer

    def factorize(self):
        if self.ring.number != 1:
            raise ValueError("Number should be one")

        algorithm = None
        char = self.ring.field.get_char()
        if char > 0:
            from algebra.ring.polynomial.factorize.finite import \
                FactorizePolynomialFinite
            algorithm = FactorizePolynomialFinite
        elif char == 0:
            from algebra.ring.polynomial.factorize.rational import \
                FactorizePolynomialRational
            algorithm = FactorizePolynomialRational
        else:
            raise ValueError("Interesting field...")

        return algorithm(self).run()

    def gcd(self, other):
        left, right = self, other
        while not right.is_zero():
            left, right = right, left % right
        return left.monic()

    def diff(self, index):
        index = self._wrap_index(index)
        value = collections.defaultdict(int)
        for monomial, multiplier in self.value.items():
            const, mono = monomial.diff(index)
            value[mono] += const * multiplier
        return PolynomialRingElement(value=value, ring=self.ring)

    def degree(self):
        return self.lead_monomial().degree()

    def sylvester_matrix(self, other, index=0):
        assert index == 0
        degree1 = self.lead_monomial().power[index]
        degree2 = other.lead_monomial().power[index]
        m = Matrix(degree1 + degree2, degree1 + degree2)
        for i in range(degree1+1):
            for j in range(degree2):
                m[j, i+j] = self[i]
        for i in range(degree1):
            for j in range(degree2+1):
                m[degree2+i, i+j] = other[j]

        return m

    def discriminant(self, index=0):
        # multi-variable에서 disc를 계산할 인터페이스를 고민해 보자
        assert self.ring.number == 1

        det = self.sylvester_matrix(self.diff(index)).determinant()

        lc = self.lead_coefficient()
        degree = self.degree()

        if (degree * (degree - 1)) % 4 == 0:
            sign = 1
        else:
            sign = -1

        return det * sign / lc

    def discriminant2(self, monomial):
        if isinstance(monomial, PolynomialRingElement):
            monomial = monomial.lead_monomial()

        if not isinstance(monomial, Monomial):
            raise TypeError("Monomial")

        d = self.max_degree(monomial)
        if (d * (d - 1)) % 4 == 0:
            s = 1
        else:
            s = -1

        f = self
        g = f.diff(monomial)
        u = v = 1

        while g.max_degree(monomial) > 0:
            delta = f.max_degree(monomial) - g.max_degree(monomial)
            g_lead = g.max_degree_coefficient(monomial)

            r = ((g_lead ** (delta + 1)) * f) % g

            f, g = g, r / (u * v ** delta)

            if g.max_degree(monomial) == 0:
                u = g.max_degree_coefficient(monomial)
                delta = f.max_degree(monomial)
            else:
                u = f.max_degree_coefficient(monomial)

            v *= (u / v) ** delta

        return s * v

    def max_degree_coefficient(self, monomial):
        return self.projection(monomial, self.max_degree(monomial))

    def max_degree(self, monomial):
        index = monomial.index()

        mono_list = [
            mono.power[index]
            for mono in self.value
        ]
        if mono_list:
            return max(mono_list)
        else:
            return 0

    def convert(self, ring: 'PolynomialRing'):
        d = {}

        for m, v in self.value.items():
            m_new = copy.copy(m)
            m_new.ring = ring
            v_new = v.convert(ring.field)
            d[m_new] = v_new

        return PolynomialRingElement(ring=ring, value=d)

    def galois_group(self):
        from algebra.ring.polynomial.galois import GaloisGroupConstructor
        return GaloisGroupConstructor(self).run()

    def projection(self, index, power_v):
        index = self._wrap_index(index)

        power = [0] * self.ring.number
        power[index] = power_v

        mon = Monomial(power=power, ring=self.ring)
        d = {}
        for m, v in self.value.items():
            if m.power[index] == power_v:
                d[m / mon] = v
        return PolynomialRingElement(ring=self.ring, value=d)

    def projection_ring(self, index):
        index = self._wrap_index(index)
        coefficient = collections.defaultdict(int)
        for monomial, value in self.value.items():
            coefficient[monomial.power[index]] += value

        pr = PolynomialRing(field=self.ring.field, number=1)
        return pr.element(coefficient)

    def is_constant(self):
        return self.degree() == 0

    @property
    def monomial_key(self):
        return self.ring.variable_system.get_key

    def _wrap_index(self, monomial):
        if isinstance(monomial, Monomial):
            return monomial.index()
        elif isinstance(monomial, int):
            return monomial
        elif isinstance(monomial, PolynomialRingElement):
            return monomial.lead_monomial().index()
        else:
            raise TypeError(f"Unknown Type : {type(monomial)}")


class Monomial(BaseModel):
    power: List[int]
    ring: 'PolynomialRing'

    def model_post_init(self, __context):
        for i, p in enumerate(self.power):
            if p < 0:
                raise ValueError(f"{i}-th index is negative.")

    def __hash__(self):
        return hash((tuple(self.power), self.ring))

    @iter_to_str
    def __str__(self):
        for index, power in enumerate(self.power):
            if power == 0:
                continue
            yield self.ring.variable_system.get_name(index)
            if power > 1:
                yield f'^{power}'

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

    def __call__(self, value_list):
        if len(self.power) != len(value_list):
            raise ValueError("Dimension not matched")

        result = 1
        for p, v in zip(self.power, value_list):
            result *= v ** p
        return result

    def degree(self):
        return sum(self.power)

    def index(self):
        if self.degree() != 1:
            raise ValueError("Degree")

        return self.power.index(1)

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

    def diff(self, index: int):
        power = list(self.power)
        const = self.ring.field.element(power[index])
        if power[index] > 0:
            power[index] -= 1
        else:
            power = [0] * len(self.power)
        return const, Monomial(power=power, ring=self.ring)

    def root(self, degree):
        for p in self.power:
            if p % degree != 0:
                raise ValueError("Root not Valid")

        return Monomial(
            power=[p // degree for p in self.power],
            ring=self.ring
        )


class PolynomialIdeal(Ideal):
    generator: list[PolynomialRingElement]
    _algorithm = None

    def is_contained(self, element):
        element = self.algorithm.get_reduce(element)
        return element.is_zero()

    def degree(self):
        return self.algorithm.degree

    def grobner_base(self):
        return self.algorithm.get_basis()

    def __rmod__(self, other):
        return self.algorithm.get_reduce(other, monic=False)

    def __truediv__(self, other):
        if not isinstance(other, PolynomialRingElement):
            return NotImplemented

        generator = [other]
        if self._algorithm is None:
            generator.extend(self.generator)
        else:
            generator.extend(self._algorithm.get_basis())

        return PolynomialIdeal(ring=self.ring, generator=generator)

    @property
    def algorithm(self):
        if self._algorithm is None:
            from algebra.ring.polynomial.buchberger import BuchbergerAlgorithm
            self._algorithm = BuchbergerAlgorithm(self.generator)
            self._algorithm.run()

        return self._algorithm


class PolynomialQuotientRing(QuotientRing):
    parent: PolynomialRing
    ideal: PolynomialIdeal

    def element(self, *args):
        parent = super().element(*args)
        return PolynomialQuotientRingElement(ring=self, element=parent.element)


class PolynomialQuotientRingElement(QuotientRingElement):
    ring: PolynomialQuotientRing
    element: PolynomialRingElement

    def minimal_polynomial(self):
        return self.ring.ideal.algorithm.minimal_polynomial(self.element)
