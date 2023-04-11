from algebra.group.abstract.permutation import PermutationGroupRep


def symmetric_group(n: int):
    if not isinstance(n, int):
        raise TypeError("Integer should be given")

    if n <= 0:
        raise ValueError("Positive integer should be given")

    rep = PermutationGroupRep(n)

    if n == 1:
        return rep.group()

    elif n == 2:
        return rep.group_([[[0, 1]]])

    return rep.group_([
        [list(range(n))],
        [[0, 1]]
    ])
