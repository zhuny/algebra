from dataclasses import dataclass
from typing import Type

from algebra.ring.base import Ring, RingElement


@dataclass
class Ideal:
    ring: Ring
    generator: list[RingElement]

    def is_equivalent(self, element1, element2):
        return self.is_contained(element1 - element2)

    def is_contained(self, element):
        raise NotImplementedError(self)


@dataclass
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


@dataclass
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
        return QuotientRingElement(
            ring=self.ring,
            element=self.element + other.element
        )

    def __neg__(self):
        return QuotientRingElement(
            ring=self.ring,
            element=-self.element
        )

    def __mul__(self, other):
        return QuotientRingElement(
            ring=self.ring,
            element=self.element * other.element
        )

    def __eq__(self, other):
        return self.ring.ideal.is_equivalent(
            self.element, other.element
        )
