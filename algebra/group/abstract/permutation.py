from dataclasses import dataclass, field
from typing import Dict

from algebra.group.abstract.base import GroupRep, GroupElement


@dataclass
class PermutationObject:
    permutation: 'PermutationGroupRep'
    value: int

    def __hash__(self):
        return hash((self.value, self.permutation))


@dataclass
class PermutationGroupRep(GroupRep):
    degree: int

    def __hash__(self):
        return hash(f"PGR{self.degree}")

    @property
    def identity(self):
        return PermutationGroupElement(group=self)

    def object_list(self):
        for i in range(self.degree):
            yield PermutationObject(
                permutation=self,
                value=i
            )

    def element(self, *args):
        if args:
            if isinstance(args[0], PermutationObject):
                args = [args]

        i = self.identity
        for seq in args:
            if len(set(seq)) != len(seq):
                raise ValueError("Sequence has a unique value")

            d = {}
            for a, b in zip(seq, seq[1:] + seq[:1]):
                d[a] = b

            i += PermutationGroupElement(group=self, perm_map=d)

        return i


@dataclass
class PermutationGroupElement(GroupElement):
    group: PermutationGroupRep
    perm_map: Dict[
        PermutationObject,
        PermutationObject
    ] = field(default_factory=dict)

    def __add__(self, other: 'PermutationGroupElement'):
        s = set(self.perm_map) | set(other.perm_map)
        d = {}
        for e1 in s:
            e2 = other._get(self._get(e1))
            if e1 != e2:
                d[e1] = e2
        return PermutationGroupElement(group=self.group, perm_map=d)

    def __neg__(self):
        return PermutationGroupElement(
            group=self.group,
            perm_map={v: k for k, v in self.perm_map.items()}
        )

    def _get(self, e):
        return self.perm_map.get(e, e)
