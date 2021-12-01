import collections
import math
from typing import Dict


class DictVector(collections.defaultdict):
    def __init__(self):
        super().__init__(int)

    def update_add(self, vector: Dict[int, int], scale=1):
        for k, v in vector.items():
            self[k] += v * scale


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

    return relation_list, generating_list


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
