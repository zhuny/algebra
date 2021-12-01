import collections
import math
from typing import Dict


class DictVector(collections.defaultdict):
    def __init__(self):
        super().__init__(int)

    def update_add(self, vector: Dict[int, int], scale=1):
        for k, v in vector.items():
            self[k] += v * scale

    def __mul__(self, other):
        result = DictVector()
        for k, v in self.items():
            result[k] = v*other
        return result

    def __add__(self, other):
        result = DictVector()
        result.update_add(self)
        result.update_add(other)
        return result


def power_series(num, m):
    current = num
    count = 1
    while True:
        yield current, count
        current = (current * num) % m
        count += 1


def multiple_group_structure(n):
    assert 2 <= n

    info: Dict[int, DictVector] = {1: DictVector()}

    # cover every element
    relation_list = []
    generating_list = []
    for i in range(2, n):
        if math.gcd(i, n) == 1 and i not in info:
            index = len(generating_list)
            already_items = list(info.items())
            for num, p in power_series(i, n):
                if num in info:
                    relation = DictVector()
                    relation[index] = p
                    relation.update_add(info[num], -1)
                    relation_list.append(relation)
                    generating_list.append(i)
                    break

                current_power_info = DictVector()
                current_power_info[index] = p
                for already_num, already_power in already_items:
                    result = DictVector()
                    result.update_add(current_power_info)
                    result.update_add(already_power)
                    info[(already_num * num) % n] = result

    # calculate smith normal form
    for index, relation in enumerate(relation_list):
        for index2, another in enumerate(relation_list[index+1:], index+1):
            if another[index] != 0:
                a, b = relation[index], another[index]
                c, d = gcd_pair_up(a, b)
                g = a*c + b*d
                aa, bb = a//g, b//g
                relation, another = (
                    relation*c + another*d,
                    relation*(-bb) + another*aa
                )
                relation_list[index2] = another
        relation_list[index] = relation

    return [
        relation[index]
        for index, relation in enumerate(relation_list)
    ], generating_list


def _gcd_pair_positive(a, b):
    s_, s = 1, 0
    t_, t = 0, 1

    while b != 0:
        q, r = divmod(a, b)
        s_, s = s, s_ - s * q
        t_, t = t, t_ - t * q
        a, b = b, r  # r = a - b * q
    return s_, t_


def gcd_pair(a, b):
    a_sign = a > 0
    b_sign = b > 0
    c, d = _gcd_pair_positive(abs(a), abs(b))
    if not a_sign:
        c = -c
    if not b_sign:
        d = -d
    return c, d


def gcd_pair_up(a, b):
    c, d = gcd_pair(a, b)
    return c-b, d+a


def run():
    """
    known facts:
        U(102) = C(16) X C(2)
        U(96) = C(8) X C(2) X C(2)
        U(80) = C(4) X C(4) X C(2)
        U(120) = C(4) X C(2) X C(2) X C(2)
    :return:
    """
    for i in [102, 96, 80, 120, 7]:
        print(i)
        print(multiple_group_structure(i))


if __name__ == '__main__':
    run()
