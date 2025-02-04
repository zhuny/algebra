from pydantic import BaseModel
from typing import Type

from algebra.ring.base import Ring, RingElement


class Ideal(BaseModel):
    ring: Ring
    generator: list[RingElement]

    def is_equivalent(self, element1, element2):
        return self.is_contained(element1 - element2)

    def is_contained(self, element):
        raise NotImplementedError(self)


class QuotientRing(Ring):
    parent: Ring
    ideal: Ideal

    def element(self, *args):
        if len(args) == 1 and isinstance(args[0], RingElement):
            element = args[0]
        else:
            element = self.parent.element(*args)

        return QuotientRingElement(ring=self, element=element)

    def zero(self):
        return self.element(0)

    def one(self):
        return self.element(1)


class QuotientRingElement(RingElement):
    ring: QuotientRing
    element: RingElement

    def is_zero(self):
        return self.ring.ideal.is_equivalent(
            self.element,
            self.ring.parent.zero()
        )

    def is_one(self):
        return self.ring.ideal.is_equivalent(
            self.element,
            self.ring.parent.one()
        )

    def __add__(self, other):
        if not self._is_valid_value(other):
            raise ValueError("Ring not matched")

        return QuotientRingElement(
            ring=self.ring,
            element=self.element + self._wrap_value(other)
        )

    def __neg__(self):
        return QuotientRingElement(
            ring=self.ring,
            element=-self.element
        )

    def __mul__(self, other):
        if not self._is_valid_value(other):
            raise ValueError("Ring not matched")

        return QuotientRingElement(
            ring=self.ring,
            element=self.element * self._wrap_value(other)
        )

    def __eq__(self, other):
        return self.ring.ideal.is_equivalent(
            self.element, other.element
        )

    def _is_valid_value(self, other):
        if isinstance(other, QuotientRingElement):
            return self.ring == other.ring
        else:
            # TODO: ring 에 element 값 확인하기
            return isinstance(other, int)

    @staticmethod
    def _wrap_value(other):
        if isinstance(other, QuotientRingElement):
            return other.element
        elif isinstance(other, int):
            return other
