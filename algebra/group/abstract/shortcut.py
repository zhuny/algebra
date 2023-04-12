from typing import Any

from algebra.group.abstract.permutation import PermutationGroupRep


def _check_positive_integer(n: Any):
    if not isinstance(n, int):
        raise TypeError("Integer should be given")

    if n <= 0:
        raise ValueError("Positive integer should be given")


def symmetric_group(n: int):
    _check_positive_integer(n)

    rep = PermutationGroupRep(n)

    if n == 1:
        return rep.group()

    elif n == 2:
        return rep.group_([[[0, 1]]])

    return rep.group_([
        [list(range(n))],
        [[0, 1]]
    ])


def alternative_group(n: int):
    _check_positive_integer(n)

    rep = PermutationGroupRep(n)

    if n < 3:
        return rep.group()

    return rep.group_([
        [[i-2, i-1, i]]
        for i in range(2, n)
    ])


def dihedral_group(n: int):
    _check_positive_integer(n)

    rep = PermutationGroupRep(n * 2)

    return rep.group_([
        [list(range(n)), list(range(n, 2 * n))[::-1]],
        [[i, n + i] for i in range(n)]
    ])
