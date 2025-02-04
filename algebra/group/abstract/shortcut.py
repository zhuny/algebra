from typing import Any

from algebra.group.abstract.permutation import PermutationGroupRep


def _check_positive_integer(n: Any):
    if not isinstance(n, int):
        raise TypeError("Integer should be given")

    if n <= 0:
        raise ValueError("Positive integer should be given")


def cyclic_group(n: int):
    assert n < 20

    rep = PermutationGroupRep(degree=n)

    if n == 1:
        return rep.group()

    return rep.group_([
        [list(range(n))]
    ])


def symmetric_group(n: int):
    _check_positive_integer(n)

    rep = PermutationGroupRep(degree=n)

    if n == 1:
        return rep.group()

    elif n == 2:
        return rep.group_([[[0, 1]]])

    return rep.group_([
        [list(range(n))],
        [[0, 1]]
    ], name=f'S({n})')


def alternative_group(n: int):
    _check_positive_integer(n)

    rep = PermutationGroupRep(degree=n)

    if n < 3:
        return rep.group()

    return rep.group_([
        [[i - 2, i - 1, i]]
        for i in range(2, n)
    ], name=f'A({n})')


def dihedral_group(n: int):
    _check_positive_integer(n)

    rep = PermutationGroupRep(degree=n * 2)

    return rep.group_([
        [list(range(n)), list(range(n, 2 * n))[::-1]],
        [[i, n + i] for i in range(n)]
    ], name=f'D({n*2})')


def quaternion_group():
    return PermutationGroupRep(degree=8).group_([
        [[0, 2, 1, 3], [4, 7, 5, 6]],  # i
        [[0, 4, 1, 5], [2, 6, 3, 7]]  # j
    ], name='Q')
