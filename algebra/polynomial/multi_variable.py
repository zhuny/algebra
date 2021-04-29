from dataclasses import dataclass, field
from typing import List, Dict

from algebra.util.zero_dict import ZeroValueSkip


@dataclass
class Monomial:
    power: List[int]
    ring: 'MultiVariableRing'

    def __hash__(self):
        return hash((tuple(self.power), self.ring))

    def __mul__(self, other):
        if isinstance(other, Monomial):
            if self.ring != other.ring:
                raise ValueError("Operation can be with same ring")

            power = [x+y for x, y in zip(self.power, other.power)]
            return Monomial(power=power, ring=self.ring)


@dataclass
class MultiVariableElement:
    ring: 'MultiVariableRing'
    coefficient: Dict[Monomial, int] = field(default_factory=dict)

    def _check(self, other):
        if self.ring != other.ring:
            raise ValueError("Operation can be with same ring")

    def __add__(self, other):
        if isinstance(other, MultiVariableElement):
            self._check(other)

        coeff = ZeroValueSkip(self.coefficient)
        if isinstance(other, MultiVariableElement):
            for mono2, c2 in other.coefficient.items():
                coeff[mono2] += c2
        else:
            one = Monomial(ring=self.ring, power=[0]*self.ring.number)
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
                    coeff[mono1*mono2] += c1*c2
            return MultiVariableElement(ring=self.ring, coefficient=dict(coeff))

        else:
            return MultiVariableElement(
                ring=self.ring,
                coefficient={k: v*other for k, v in self.coefficient.items()}
            )

    def __neg__(self):
        return MultiVariableElement(
            ring=self.ring,
            coefficient={k: -v for k, v in self.coefficient.items()}
        )

    def __rmul__(self, other):
        return self * other

    def __div__(self, other):
        return self.__divmod__(other)[0]

    def __mod__(self, other):
        return self.__divmod__(other)[1]

    def __divmod__(self, other):
        return self, other


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
