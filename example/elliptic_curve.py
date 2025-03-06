from dataclasses import dataclass

from algebra.field.base import Field, FieldElement
from algebra.field.finite_prime import FinitePrimeField
from algebra.group.abstract.base import GroupRep, Group, GroupElement


@dataclass
class EllipticCurveRep(GroupRep):
    field: Field
    a: FieldElement | int
    b: FieldElement | int

    def model_post_init(self, __context):
        self.a = self.field.element(self.a)
        self.b = self.field.element(self.b)

        d = 4 * self.a ** 3 + 27 * self.b ** 2
        if d.is_zero():
            raise ValueError("Invalid elliptic curve representation.")

    def group(self):
        return EllipticCurve(represent=self, generator=[])

    def element(self, x, y):
        x = self.field.element(x)
        y = self.field.element(y)

        left = y * y
        right = x * x * x + self.a * x + self.b
        if left != right:
            print(x, y, left, right)
            raise ValueError("Point not in Curve")

        return EllipticCurveElement1(group=self, x=x, y=y)

    @property
    def identity(self):
        return EllipticCurveElement0(group=self)


@dataclass
class EllipticCurve(Group):
    represent: EllipticCurveRep


@dataclass
class EllipticCurveElement(GroupElement):
    group: EllipticCurveRep


@dataclass
class EllipticCurveElement1(EllipticCurveElement):  # non-zero element
    x: FieldElement
    y: FieldElement

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __add__(self, other: 'EllipticCurveElement'):
        if not isinstance(other, EllipticCurveElement1):
            return NotImplemented

        other: EllipticCurveElement1
        if self == - other:
            return EllipticCurveElement0(self.group)

        s = self.x * self.x + self.x * other.x + other.x * other.x
        s += self.group.a
        s /= self.y + other.y

        new_x = s * s - self.x - other.x
        new_y = self.y - s * (self.x - new_x)

        return self.group.element(new_x, -new_y)

    def __neg__(self):
        return self.group.element(self.x, -self.y)

    def __mul__(self, other: int):
        v = self.group.identity
        for i in range(other):
            v += self
        return v


@dataclass
class EllipticCurveElement0(EllipticCurveElement):
    def __str__(self):
        return "(0)"

    def __add__(self, other: EllipticCurveElement):
        return other

    def __mul__(self, other: int):
        return self


def main():
    rep = EllipticCurveRep(FinitePrimeField(5), 1, 1)
    element = rep.element(4, 2)
    print(element + element)
    for i in range(10):
        print(i, element * i)


if __name__ == '__main__':
    main()
