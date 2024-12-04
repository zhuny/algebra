class RingBase:
    def __add__(self, other):
        raise NotImplementedError(self)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        raise NotImplementedError(self)

    def __mul__(self, other):
        raise NotImplementedError(self)

    def __rmul__(self, other):
        return self * other

    def __eq__(self, other):
        return (self - other).is_zero()

    def __ne__(self, other):
        return not (self == other)

    def is_zero(self):
        raise NotImplementedError(self)
