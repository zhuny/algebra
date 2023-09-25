from dataclasses import dataclass, field
from typing import Dict

from algebra.group.abstract.base import GroupRep, GroupElement
from algebra.number.util import lcm


@dataclass
class PermutationObject:
    permutation: 'PermutationGroupRep'
    value: int

    def __hash__(self):
        return hash((self.value, self.permutation))

    def __str__(self):
        return str(self.value)

    def __lt__(self, other):
        return self.value < other.value


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
            mapping = {}

            if isinstance(seq, (tuple, list)):
                if len(set(seq)) != len(seq):
                    raise ValueError("Sequence has a unique value")
                mapping.update(zip(seq, seq[1:] + seq[:1]))

            elif isinstance(seq, dict):
                if set(seq) != set(seq.values()):
                    raise ValueError("Should be same")
                mapping.update(seq)

            i += PermutationGroupElement(group=self, perm_map=mapping)

        return i


@dataclass
class PermutationGroupElement(GroupElement[PermutationObject]):
    group: PermutationGroupRep
    perm_map: Dict[
        PermutationObject,
        PermutationObject
    ] = field(default_factory=dict)

    def __add__(self, other: 'PermutationGroupElement'):
        s = set(self.perm_map) | set(other.perm_map)
        d = {}
        for e1 in s:
            e2 = other.act(self.act(e1))
            if e1 != e2:
                d[e1] = e2
        return PermutationGroupElement(group=self.group, perm_map=d)

    def __neg__(self):
        return PermutationGroupElement(
            group=self.group,
            perm_map={v: k for k, v in self.perm_map.items()}
        )

    def _to_seq(self):
        done = set()
        for k, v in sorted(self.perm_map.items()):
            if k in done:
                continue

            s1 = k
            one = []
            while True:
                one.append(s1.value)
                done.add(s1)
                s1 = self.perm_map[s1]
                if s1 == k:
                    break
            yield one

    def __str__(self):
        return str(list(self._to_seq()))

    def __hash__(self):
        return hash((self.group, str(self)))

    def is_identity(self) -> bool:
        return len(self.perm_map) == 0

    def act(self, o: PermutationObject) -> PermutationObject:
        return self.perm_map.get(o, o)

    def order(self) -> int:
        order = 1
        for seq in self._to_seq():
            order = lcm(order, len(seq))
        return order
