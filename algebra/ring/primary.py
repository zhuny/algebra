import functools
import math
from pydantic import BaseModel
from typing import Type, Any

from algebra.ring.base import Ring, RingElement
from algebra.ring.quotient import Ideal


class BuiltinWrapRingElement(RingElement):
    value: Any

    def is_zero(self):
        return self.value == 0

    def is_one(self):
        return self.value == 1

    def __add__(self, other):
        return self._wrap_it(self.value + other.value)

    def __neg__(self):
        return self._wrap_it(-self.value)

    def __mul__(self, other):
        return self._wrap_it(self.value * other.value)

    def _wrap_it(self, value):
        cls: Type[BuiltinWrapRingElement] = type(self)
        return cls(ring=self.ring, value=value)


################
# Integer Ring #
################
class IntegerRing(Ring):
    def element(self, number):
        return IntegerRingElement(ring=self, value=int(number))

    def zero(self):
        return self.element(0)

    def one(self):
        return self.element(1)

    def _build_ideal(self,
                     element_list: list['IntegerRingElement']
                     ) -> 'IntegerIdeal':
        return IntegerIdeal(
            ring=self,
            generator=element_list
        )


class IntegerRingElement(BuiltinWrapRingElement):
    pass


class IntegerIdeal(Ideal):
    generator: list[IntegerRingElement]

    def model_post_init(self, __context):
        if len(self.generator) == 0:
            raise ValueError("At least one element is needed")

        minimal = functools.reduce(
            math.gcd,
            [g.value for g in self.generator]
        )
        self.generator = [self.ring.element(minimal)]

    def is_contained(self, element: IntegerRingElement):
        for g in self.generator:
            if element.value % g.value == 0:
                return True
        return False
