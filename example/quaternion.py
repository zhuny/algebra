from dataclasses import dataclass

from algebra.group.abstract.permutation import PermutationGroupRep


@dataclass
class QuaternionElement:
    real: int = 0
    i: int = 0
    j: int = 0
    k: int = 0

    def __hash__(self):
        return hash(tuple(self.by_index()))

    def by_index(self):
        yield 0, self.real
        yield 1, self.i
        yield 2, self.j
        yield 3, self.k

    def _add_index(self, left_index, right_index):
        # 실수 곱셈 처리
        if left_index == 0:
            return right_index, 1
        if right_index == 0:
            return left_index, 1

        # 같은 index처리 : i+i = j+j = k+k = -1
        if left_index == right_index:
            return 0, -1

        # ij = k, jk = i, ki = j
        if self._next_index(left_index) == right_index:
            return self._next_index(right_index), 1

        # ji = -k, kj = -i, ik = -j
        if self._next_index(right_index) == left_index:
            return self._next_index(left_index), -1

        # unreachable

    def _next_index(self, index):
        # i(1) -> j(2), j(2) -> k(3), k(3) -> i(1)
        return index % 3 + 1

    def __add__(self, other):
        result = [0, 0, 0, 0]
        for l_i, l_v in self.by_index():
            for r_i, r_v in other.by_index():
                new_index, sign = self._add_index(l_i, r_i)
                result[new_index] += sign * l_v * r_v
        return QuaternionElement(*result)


def quaternion_list():
    for i in range(4):
        over = [0] * 4
        for j in [-1, 1]:
            over[i] = j
            yield QuaternionElement(*over)


def index_map_construct():
    index_map = {
        e: i
        for i, e in enumerate(quaternion_list())
    }

    for e in quaternion_list():
        element_rep = {}
        for o1 in quaternion_list():
            o2 = o1 + e
            if o1 != o2:
                element_rep[index_map[o1]] = index_map[o2]

        yield element_rep

    print('i :', index_map[QuaternionElement(0, 1, 0, 0)])
    print('j :', index_map[QuaternionElement(0, 0, 1, 0)])


def construct_quaternion():
    rep = PermutationGroupRep(8)
    ol = list(rep.object_list())

    for index_map in index_map_construct():
        element = rep.identity
        for i, j in index_map.items():
            element.perm_map[ol[i]] = ol[j]
        print(element)


if __name__ == '__main__':
    construct_quaternion()
