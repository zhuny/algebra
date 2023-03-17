from dataclasses import dataclass
from enum import Enum

from algebra.group.abstract.permutation import PermutationGroupRep


@dataclass(unsafe_hash=True)
class Point:
    x: int
    y: int
    z: int

    @classmethod
    def unit_by_axis(cls, axis: 'Axis', value: int):
        pos_value = {'x': 0, 'y': 0, 'z': 0}
        pos_value[axis.value] = value
        return cls(**pos_value)

    def get_value(self, axis: 'Axis'):
        return getattr(self, axis.value)

    def rotate(self, axis: 'Axis'):
        match_value = []
        unmatch_value = []

        for a in Axis:
            if a == axis:
                match_value.append(self.get_value(a))
            else:
                unmatch_value.append(self.get_value(a))
        unmatch_value[0] *= -1

        v = {}
        for a in Axis:
            if a == axis:
                v[a.value] = match_value.pop()
            else:
                v[a.value] = unmatch_value.pop()

        return Point(**v)

    def __add__(self, other: 'Point'):
        return Point(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def __mul__(self, other: int):
        return Point(self.x * other, self.y * other, self.z * other)


@dataclass(unsafe_hash=True)
class RubikFace:
    pos: Point
    norm: Point

    def get_value(self, axis: 'Axis'):
        return self.pos.get_value(axis)


class Axis(Enum):
    x = 'x'
    y = 'y'
    z = 'z'


@dataclass(unsafe_hash=True)
class Rotation:
    axis: Axis
    value: int

    def __call__(self, element: RubikFace):
        if element.get_value(self.axis) == self.value:
            return RubikFace(
                pos=element.pos.rotate(self.axis),
                norm=element.norm.rotate(self.axis)
            )
        return element


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

    def group(self):
        perm = PermutationGroupRep(len(self.face_list))
        ol = perm.object_list()
        face_map = dict(zip(self.face_list, ol))

        generators = []

        for rotate in self.rotate_list:
            done_face = set()
            seq = []
            for face in self.face_list:
                if face in done_face:
                    continue
                face_seq = []
                while face not in done_face:
                    face_seq.append(face_map[face])
                    done_face.add(face)
                    face = rotate(face)
                seq.append(face_seq)
            generators.append(perm.element(*seq))

        return perm.group(*generators)


def construct():
    rubik = Rubik()
    for face in rubik.face_list:
        print(face)
    for rotate in rubik.rotate_list:
        print(rotate)

    group = rubik.group()
    for gen in group.generator:
        print(gen)
    chain = group.stabilizer_chain()
    chain.show()
    print(group.order())


if __name__ == '__main__':
    construct()
