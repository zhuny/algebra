from dataclasses import dataclass
from enum import Enum


@dataclass
class Point:
    x: int
    y: int
    z: int

    @classmethod
    def unit_by_axis(cls, axis: 'Axis', value: int):
        pos_value = {'x': 0, 'y': 0, 'z': 0}
        pos_value[axis.value] = value
        return cls(**pos_value)

    def __add__(self, other: 'Point'):
        return Point(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def __mul__(self, other: int):
        return Point(self.x * other, self.y * other, self.z * other)


@dataclass
class RubikFace:
    pos: Point
    norm: Point
    index: int = -1


class Axis(Enum):
    x = 'x'
    y = 'y'
    z = 'z'


@dataclass
class Rotation:
    axis: Axis
    value: int


class Rubik:
    def __init__(self):
        self.face_list = list(self._face_list())
        self.rotate_list = list(self._rotate_list())

    def _one_face(self, norm_axis: Axis, index):
        base_list = []
        normal = None
        for axis in Axis:
            if axis == norm_axis:
                normal = Point.unit_by_axis(axis, index)
            else:
                base_list.append(Point.unit_by_axis(axis, 1))

        for x in range(-1, 2):
            for y in range(-1, 2):
                yield RubikFace(
                    pos=normal + base_list[0] * x + base_list[1] * y,
                    norm=normal
                )

    def _face_list(self):
        for axis in Axis:
            yield from self._one_face(axis, -1)
            yield from self._one_face(axis, 1)

    def _rotate_list(self):
        for axis in Axis:
            yield Rotation(axis, -1)
            yield Rotation(axis, 1)


def construct():
    rubik = Rubik()
    print(rubik.face_list)
    print(rubik.rotate_list)


if __name__ == '__main__':
    construct()
