import pydantic
from pydantic import BaseModel
from typing import Dict, Type

from algebra.group.abstract.base import GroupRep, GroupElement
from algebra.number.util import lcm


class PermutationObject(BaseModel):
    permutation: 'PermutationGroupRep'
    value: int

    def __hash__(self):
        return hash((self.value, self.permutation))

    def __str__(self):
        return str(self.value)

    def __lt__(self, other):
        return self.value < other.value


class PermutationGroupRep(GroupRep):
    degree: int

    def __hash__(self):
        return id(self)

    @property
    def identity(self):
        return self.cls_element(group=self)

    @property
    def cls_element(self) -> Type:
        return PermutationGroupElement

    def object_list(self):
        for i in range(self.degree):
            yield PermutationObject(permutation=self, value=i)

    def check_object(self, o: PermutationObject):
        if o.permutation != self:
            raise ValueError('Permutation Not Correct')

    def element(self, element):
        i = self.identity

        for seq in element:
            mapping = {}

            if isinstance(seq, (tuple, list)):
                if len(set(seq)) != len(seq):
                    raise ValueError("Sequence has a unique value")
                mapping.update(zip(seq, seq[1:] + seq[:1]))

            elif isinstance(seq, dict):
                if set(seq) != set(seq.values()):
                    raise ValueError("Should be same")
                mapping.update(seq)

            else:
                raise ValueError("Should be a dict or list")

            new_mapping = {
                self._wrap_object(k): self._wrap_object(v)
                for k, v in mapping.items()
            }

            i += self.cls_element(group=self, perm_map=new_mapping)

        return i

    def as_group(self):
        return self.group_([[[0, 1]], [list(range(self.degree))]])

    def _wrap_object(self, o):
        if isinstance(o, int):
            o = PermutationObject(permutation=self, value=o)
        if not isinstance(o, PermutationObject):
            raise TypeError("Should be a PermutationObject")
        return o


class PermutationGroupElement(GroupElement):
    group: PermutationGroupRep
    perm_map: Dict[
        PermutationObject,
        PermutationObject
    ] = pydantic.Field(default_factory=dict)

    def __add__(self, other: 'PermutationGroupElement'):
        s = set(self.perm_map) | set(other.perm_map)
        d = {}
        for e1 in s:
            e2 = other.act(self.act(e1))
            if e1 != e2:
                d[e1] = e2
        return self.cls_element(group=self.group, perm_map=d)

    def __neg__(self):
        return self.cls_element(
            group=self.group,
            perm_map={v: k for k, v in self.perm_map.items()}
        )

    def to_seq(self):
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
        return str(list(self.to_seq()))

    def __hash__(self):
        return hash((self.group, str(self)))

    def is_identity(self) -> bool:
        return len(self.perm_map) == 0

    def act(self, o: PermutationObject) -> PermutationObject:
        return self.perm_map.get(o, o)

    def order(self) -> int:
        order = 1
        for seq in self.to_seq():
            order = lcm(order, len(seq))
        return order

    def orbit(self, o: PermutationObject) -> list[PermutationObject]:
        o_list = [o]
        o_c = self.act(o)
        while o_c != o:
            o_list.append(o_c)
            o_c = self.act(o_c)
        return o_list

    def orbit_list(self):
        return len(list(self.to_seq()))

    @property
    def cls_element(self) -> Type:
        return type(self)
