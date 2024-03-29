from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Dict

from algebra.number.types import Number, NumberType
from algebra.util.zero_dict import ZeroValueSkip


@dataclass(order=True)  # order can be diff by user.
class Monomial:
    power: List[int]
    ring: 'MultiVariableRing'

    def __post_init__(self):
        for i, p in enumerate(self.power):
            if p < 0:
                raise ValueError(f"{i}-th index is negative.")

    def __hash__(self):
        return hash((tuple(self.power), self.ring))

    def __mul__(self, other):
        if isinstance(other, Monomial):
            if self.ring != other.ring:
                raise ValueError("Operation can be with same ring")

            power = [x + y for x, y in zip(self.power, other.power)]
            return Monomial(power=power, ring=self.ring)

    def __truediv__(self, other):
        if not self.is_divisible(other):
            raise ValueError("Cannot Divisible")
        if self.ring != other.ring:
            raise ValueError("Operation can be with same ring")

        power = [x - y for x, y in zip(self.power, other.power)]
        return Monomial(power=power, ring=self.ring)

    def is_divisible(self, other: 'Monomial'):
        if self.ring != other.ring:
            raise ValueError("Operation can be with same ring")

        for x, y in zip(self.power, other.power):
            if x < y:
                return False
        return True


@dataclass
class MultiVariableElement:
    ring: 'MultiVariableRing'
    coefficient: Dict[Monomial, Number] = field(default_factory=dict)

    def __post_init__(self):
        for m, v in list(self.coefficient.items()):
            if not isinstance(v, Fraction):
                v = Fraction(v)
            if v == 0:
                self.coefficient.pop(m)
            else:
                self.coefficient[m] = v

    def _check(self, other):
        if self.ring != other.ring:
            raise ValueError("Operation can be with same ring")

    def __eq__(self, other):
        if isinstance(other, NumberType):
            other = self.ring.constant(other)

        if not isinstance(other, MultiVariableElement):
            raise TypeError('Unknown Type Error')

        return (
            self.ring == other.ring and
            self.coefficient == other.coefficient
        )

    def __getitem__(self, item):
        if isinstance(item, Monomial):
            if item.ring == self.ring:
                if item in self.coefficient:
                    return self.coefficient[item]
                else:
                    return Fraction()
            else:
                raise ValueError('Monomial is not defined on same ring')
        else:
            raise ValueError('Only monomial can be used')

    def __add__(self, other):
        if isinstance(other, MultiVariableElement):
            self._check(other)

        coeff = ZeroValueSkip(self.coefficient)
        if isinstance(other, MultiVariableElement):
            for mono2, c2 in other.coefficient.items():
                coeff[mono2] += c2
        else:
            one = Monomial(ring=self.ring, power=[0] * self.ring.number)
            coeff[one] += other

        return MultiVariableElement(ring=self.ring, coefficient=dict(coeff))

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if isinstance(other, MultiVariableElement):
            self._check(other)

            coeff = ZeroValueSkip()
            for mono1, c1 in self.coefficient.items():
                for mono2, c2 in other.coefficient.items():
                    coeff[mono1 * mono2] += c1 * c2
            return MultiVariableElement(ring=self.ring,
                                        coefficient=dict(coeff))

        else:
            return MultiVariableElement(
                ring=self.ring,
                coefficient={k: v * other for k, v in self.coefficient.items()}
            )

    def __neg__(self):
        return MultiVariableElement(
            ring=self.ring,
            coefficient={k: -v for k, v in self.coefficient.items()}
        )

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, MultiVariableElement):
            return self.__divmod__(other)[0]
        else:
            return MultiVariableElement(
                ring=self.ring,
                coefficient={
                    k: v / other
                    for k, v in self.coefficient.items()
                }
            )

    def __mod__(self, other):
        return self.__divmod__(other)[1]

    def __divmod__(self, other: 'MultiVariableElement'):
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
                    divisible = MultiVariableElement(
                        ring=self.ring, coefficient={monomial: coefficient})
                    current -= divisible * other
                    break
            else:  # if current is not changed, stop iteration.
                break

        return (
            MultiVariableElement(ring=self.ring, coefficient=result),
            current
        )

    def lead_monomial(self):
        if self.coefficient:
            return max(self.coefficient)
        else:
            return Monomial(ring=self.ring, power=[0] * self.ring.number)

    def lead_coefficient(self):
        if self.coefficient:
            return self.coefficient[max(self.coefficient)]
        else:
            return Fraction()

    def lead_term(self):
        lm = max(self.coefficient)
        lc = self.coefficient[lm]
        return MultiVariableElement(ring=self.ring, coefficient={lm: lc})

    def sorted_term(self):
        yield from sorted(self.coefficient.items(), reverse=True)


@dataclass(unsafe_hash=True)
class MultiVariableRing:
    # TODO: variable name
    # TODO: setting monomial ordering. Now, use lexical order
    number: int  # the number of variables.

    def variables(self):
        for i in range(self.number):
            power = [0] * self.number
            power[i] = 1
            yield MultiVariableElement(
                ring=self,
                coefficient={
                    Monomial(power=power, ring=self): 1
                }
            )

    def constant(self, number: Number):
        if not isinstance(number, NumberType):
            raise TypeError(f'Number should be given but {number!r}')
        return MultiVariableElement(
            ring=self,
            coefficient={
                Monomial(power=[0] * self.number, ring=self): number
            }
        )
