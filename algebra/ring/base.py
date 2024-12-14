from dataclasses import dataclass


@dataclass
class Ring:
    def element(self, *args):
        raise NotImplementedError(self)

    def zero(self):
        raise NotImplementedError(self)

    def one(self):
        raise NotImplementedError(self)

    def __truediv__(self, ideal):
        from algebra.ring.quotient import Ideal, QuotientRing

        if not isinstance(ideal, Ideal):
            raise TypeError("Ideal should be given")

        return QuotientRing(parent=self, ideal=ideal)

    def ideal(self, element_list: list['RingElement']):
        for element in element_list:
            if element.ring != self:
                raise ValueError("Elements should be element of self")

        return self._build_ideal(element_list)

    def _build_ideal(self, element_list: list['RingElement']):
        raise NotImplementedError(self)


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

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        raise NotImplementedError(self)

    def __mul__(self, other):
        raise NotImplementedError(self)

    def __pow__(self, power, modulo=None):
        if not (isinstance(power, int) and power >= 1):
            return NotImplemented

        # TODO: More efficient implementation needed
        current = self
        for i in range(1, power):
            current *= self
        return current
