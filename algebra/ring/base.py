from dataclasses import dataclass


@dataclass
class Ring:
    def element(self, *args):
        raise NotImplementedError(self)

    def zero(self):
        raise NotImplementedError(self)

    def one(self):
        raise NotImplementedError(self)

    def __truediv__(self, other):
        from algebra.ring.quotient import Ideal, QuotientRing
        assert isinstance(other, Ideal)

        return QuotientRing(parent=self, ideal=other)


@dataclass
class RingElement:
    ring: Ring

    def is_zero(self):
        """
        Identity of addition
        """
        raise NotImplementedError(self)

    def is_one(self):
        """
        Identity of multiply
        """
        raise NotImplementedError(self)

    def __add__(self, other):
        raise NotImplementedError(self)

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        raise NotImplementedError(self)

    def __mul__(self, other):
        raise NotImplementedError(self)
