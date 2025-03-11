import functools
from operator import index

import pydantic
from pydantic import BaseModel
from typing import Dict, Type, TypeVar, Set, Iterator

from algebra.group.abstract.base import GroupRep, GroupElement, Group, \
    GroupElementPair
from algebra.number.util import lcm


T = TypeVar('T')


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
        return self.element_cls(represent=self, perm_map={})

    @property
    def group_cls(self) -> Type:
        return PermutationGroup

    @property
    def element_cls(self) -> Type:
        return PermutationGroupElement

    def object_list(self):
        for i in range(self.degree):
            yield PermutationObject(permutation=self, value=i)

    def check_object(self, o: PermutationObject):
        if o.permutation != self:
            raise ValueError('Permutation Not Correct')

    def element(self, element):
        if isinstance(element, self.element_cls):
            return element

        i = self.identity

        for seq in element:
            mapping = {}

            if isinstance(seq, (tuple, list, range)):
                if isinstance(seq, range):
                    seq = list(seq)
                for e in seq:
                    if not isinstance(e, int):
                        raise ValueError("Element should be int")
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

            i += self.element_cls(represent=self, perm_map=new_mapping)

        return i

    def as_group(self):
        return self.group([[[0, 1]], [list(range(self.degree))]])

    def _wrap_object(self, o):
        if isinstance(o, int):
            o = PermutationObject(permutation=self, value=o)
        if not isinstance(o, PermutationObject):
            raise TypeError("Should be a PermutationObject")
        return o


class PermutationGroupElement(GroupElement):
    represent: PermutationGroupRep
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
        return self.cls_element(represent=self.represent, perm_map=d)

    def __neg__(self):
        return self.cls_element(
            represent=self.represent,
            perm_map={v: k for k, v in self.perm_map.items()}
        )

    def __mul__(self, other):
        if not isinstance(other, int):
            return NotImplemented()

        current = self
        for i in range(1, other):
            current += self
        return current

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
        return hash((self.represent, str(self)))

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


class PermutationGroup(Group):
    represent: PermutationGroupRep
    generator: list['PermutationGroupElement']

    def element_list(self) -> Iterator['GroupElement']:
        return StabilizerTraveler(self).visit()

    def order(self):
        return self.stabilizer_chain.order

    def element_test(self, element: 'GroupElement'):
        return self.stabilizer_chain.element_test(element)

    def random_element(self) -> 'GroupElement':
        element = self.represent.identity
        for stabilizer in self.stabilizer_chain.travel():
            if stabilizer.is_trivial():
                break
            info = random.choice(list(stabilizer.transversal.values()))
            element += info.element
        return element

    def factor(self, element: 'GroupElement'):
        chain = self.stabilizer_chain(True)
        if not self.element_test(element):
            raise ValueError('Element not in the Group')

        return chain.factor(element)

    def normal_closure(self, element_list: list['GroupElement']):
        for element in element_list:
            if not self.element_test(element):
                raise ValueError('Element should be belong to this group')

        chain = StabilizerChain(group=self.represent.group())
        obj_iter = ElementContainer(self.represent.object_list())

        insert_queue = set(element_list)
        while insert_queue:
            element = insert_queue.pop()

            for generator in self.generator:
                new_element = -generator + element + generator
                if not chain.element_test(new_element):
                    chain.extend(new_element, obj_iter)
                    insert_queue.add(new_element)

        return chain.construct()

    def stabilizer(self, o: T) -> 'Group':
        self.represent.check_object(o)

        done = set()
        queue = {o}
        transversal = {o: self.represent.identity}

        new_generator = []
        while queue:
            c = queue.pop()
            done.add(c)
            for g in self.generator:
                gc = g.act(c)
                if gc not in done:
                    transversal[gc] = transversal[c] + g
                    queue.add(gc)
                else:
                    new_generator.append(
                        transversal[c] + g - transversal[gc]
                    )

        return Group(
            represent=self.represent,
            generator=[
                g
                for g in new_generator
                if not g.is_identity()
            ]
        )

    def stabilizer_many(self, obj_list: list[T]) -> 'Group':
        current = self
        for obj in obj_list:
            current = current.stabilizer(obj)
        return current

    @functools.cached_property
    def stabilizer_chain(self) -> 'StabilizerChain':
        from algebra.group.abstract.permutation.stabilizer import \
            StabilizerChain, \
            ElementContainer

        chain = StabilizerChain(
            group=self.represent.group(),
            is_factor=False
        )
        obj_iter = ElementContainer(self.represent.object_list())
        for g in self.generator:
            chain.extend(g, obj_iter)

        return chain

    def stabilize_pair(self, rep: GroupRep, pair_list: list[GroupElementPair]):
        # stabilize for every object in this represent

        current_pair_list = pair_list
        if len(pair_list) == 0:
            return

        pair_identity = GroupElementPair(
            source=self.represent.identity,
            target=rep.identity
        )

        for o in self.represent.object_list():
            queue = {o}
            traversal = {o: pair_identity}
            new_pair_list = []

            while queue:
                c = queue.pop()
                for pair in current_pair_list:
                    gc = pair.source.act(c)
                    if gc not in traversal:
                        traversal[gc] = traversal[c] + pair
                        queue.add(gc)
                    else:
                        new_element = traversal[c] + pair - traversal[gc]
                        if new_element.is_identity():
                            continue
                        new_pair_list.append(new_element)

            current_pair_list = new_pair_list

        return current_pair_list

    def center(self):
        chain = StabilizerChain(group=self.represent.group())
        obj_iter = ElementContainer(self.represent.object_list())

        for element in self.element_list():
            if self.is_commute(element):
                if not chain.element_test(element):
                    chain.extend(element, obj_iter)

        return chain.construct()

    def orbit(self, o: T) -> Set[T]:
        done = set()
        queue = {o}
        while queue:
            c = queue.pop()
            done.add(c)
            for g in self.generator:
                gc = g.act(c)
                if gc not in done:
                    queue.add(gc)
        return done

    def orbit_list(self):
        o_done = set()
        o_list = []

        for o in self.represent.object_list():
            if o in o_done:
                continue

            orbit = self.orbit(o)
            if len(orbit) > 1:
                o_list.append(orbit)
            o_done.update(orbit)

        return o_list

    def _get_abelian_key_gen(self):
        return StabilizerOrderTraveler(self).visit()
