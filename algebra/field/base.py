from pydantic import BaseModel


class Field(BaseModel):
    def element(self, *args) -> 'FieldElement':
        raise NotImplementedError(type(self))

    def zero(self):
        return self.element(0)

    def one(self):
        return self.element(1)

    def get_char(self):
        raise NotImplementedError(type(self))


class FieldElement(BaseModel):
    field: Field

    def __str__(self):
        raise NotImplementedError(type(self))

    def __add__(self, other):
        raise NotImplementedError(type(self))

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        raise NotImplementedError(type(self))

    def __mul__(self, other):
        raise NotImplementedError(type(self))

    def __truediv__(self, other):
        return self * other.inv()

    def __rtruediv__(self, other):
        return other * self.inv()

    def __eq__(self, other):
        return (self - other).is_zero()

    def inv(self):
        raise NotImplementedError(type(self))

    def is_zero(self):
        raise NotImplementedError(type(self))

    def is_one(self):
        raise NotImplementedError(type(self))

    def convert(self, another):
        raise NotImplementedError(self, another)
