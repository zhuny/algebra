import itertools
from functools import singledispatchmethod
from typing import Any

import pydantic
from pydantic import BaseModel

from algebra.group.abstract.automorphism import AutomorphismGroupRep, \
    AutomorphismMap
from algebra.group.abstract.base import GroupElement, GroupRep, Group
from algebra.group.abstract.polycyclic.reduced import PolyCyclicRowReduced


class PolyCyclicGroupRep(GroupRep):
    degree: int
    number: int
    power_relation: dict[int, list[int]] = pydantic.Field(
        default_factory=dict
    )
    commute_relation: dict[tuple[int, int], list[int]] = pydantic.Field(
        default_factory=dict
    )

    @property
    def group_cls(self):
        return PolyCyclicGroup

    def element(self, power):
        return PolyCyclicGroupElement(group=self, power=power)

    @property
    def identity(self):
        return self.element([0] * self.number)

    def from_index(self, index):
        power = [0] * self.number
        power[index] = 1
        return self.element(power)

    def as_group(self):
        return self.group(self.generator_list())

    def add_number(self):
        n = self.number
        self.number += 1
        return n

    def generator_list(self, count=1):
        gen_list = [self.from_index(i) for i in range(self.number)]
        if count == 1:
            return gen_list
        return itertools.combinations(gen_list, count)

    def _remove_index(self, index, sub_rel):
        rel_map = {}
        for k in range(self.number):
            if k < index:
                rel_map[k] = [k]
            elif k == index:
                rel_map[k] = sub_rel
            else:
                rel_map[k] = [k - 1]
        self.power_relation = self._remove_index_obj(
            self.power_relation, rel_map
        )
        self.commute_relation = self._remove_index_obj(
            self.commute_relation, rel_map
        )
        self.number -= 1

    def _remove_index_obj(self, o, rel_map):
        if isinstance(o, int):
            return rel_map[o][0]
        elif isinstance(o, (tuple, list)):
            o_ = []
            for i in o:
                o_.extend(rel_map[i])
            if isinstance(o, tuple):
                o_ = tuple(o_)
            return o_
        elif isinstance(o, dict):
            o_ = {}
            for k, v in o.items():
                k = self._remove_index_obj(k, rel_map)
                v = self._remove_index_obj(v, rel_map)
                if v:
                    o_[k] = v
            return o_
        else:
            raise TypeError

    def show(self, msg=None):
        if msg:
            print(msg)
        print(f'PCG({self.degree}, {self.number}) with..')
        for i, rel in self.power_relation.items():
            print(i, rel)
        for (j, i), rel in self.commute_relation.items():
            print(j, i, rel)


class PolyCyclicGroup(Group):
    generator: list['PolyCyclicGroupElement']

    def __hash__(self):
        return hash((id(self.represent), str(self)))

    def __truediv__(self, other: 'PolyCyclicGroup'):
        assert self.represent is other.represent

        # 몇몇 index를 제거 하기 위한 reduce 구성
        right_align = PolyCyclicRowReduced(align=True)
        for g in other.generator:
            right_align.append_mult(g)

        new_rep = self.represent.model_copy(deep=True)
        for index, element in right_align.get_sorted_map():
            new_rel = self.represent.from_index(index) - element.element
            new_rep._remove_index(index, new_rel.to_index_list())

        generator_list = []
        for g in self.generator:
            row = right_align.reduce(g)
            new_index = right_align.pop_index(row)
            generator_list.append(new_index)

        return new_rep.group(generator_list)

    def model_post_init(self, __context):
        reduced = PolyCyclicRowReduced()  # 두고두고 쓸 듯
        for g in self.generator:
            reduced.append_mult(g)
        reduced.arrange_reverse()

        self.generator = reduced.get_reduced()

    def p_covering_group(self):
        from algebra.group.abstract.polycyclic.p_convering import \
            PCoveringGroupAlgorithm

        return PCoveringGroupAlgorithm(self).run()

    def lower_exponent_p_central_series(self):
        current = self
        yield current

        while not current.is_trivial():
            current = self.lower_exponent_p_central(current)
            yield current

    def lower_exponent_p_central(self, other: 'PolyCyclicGroup' = None):
        if other is None:
            other = self

        generator_list = []
        for g1 in self.generator:
            for h in other.generator:
                for g2 in other.generator:
                    generator_list.append(
                        g1 + h - g1 - h +
                        g2 * self.represent.degree
                    )

        return PolyCyclicGroup(
            represent=self.represent,
            generator=generator_list
        )

    def automorphism_group(self):
        exponent_series = list(self.lower_exponent_p_central_series())

        exponent_series.pop(0)  # == self
        frattini = exponent_series.pop(0)

        free_number = len(self.generator) - len(frattini.generator)
        auto_group_rep = AutomorphismGroupRep(structure=self)
        auto_group_gen = []

        for g1, g2 in itertools.combinations(self.generator[:free_number], 2):
            auto_group_gen.append({g1: g1 + g2, g2: g2})
            auto_group_gen.append({g1: g2, g2: g1})

        if len(exponent_series) > 1:
            assert False

        return auto_group_rep.group([
            PolyCyclicAutomorphismMap(group_element_map=gen)
            for gen in auto_group_gen
        ])

    def order(self):
        return pow(self.represent.degree, len(self.generator))

    def subgroup_list(self):
        element_list = [self.represent.identity]
        for generator in self.generator:
            element_list.extend([
                element + generator
                for element in element_list
            ])

        subgroup_list = {self.represent.group([])}
        for element in element_list:
            for subgroup in list(subgroup_list):
                subgroup_list.add(subgroup.append(element))

        return subgroup_list

    def _get_abelian_key_gen(self):
        group = self.represent.group()
        for generator in self.generator:
            if group.element_test(generator):
                continue
            group = group.append(generator)
            yield generator.order()

    def element_test(self, element: 'GroupElement'):
        reduced = PolyCyclicRowReduced()
        for g in self.generator:
            reduced.append_mult(g)
        reduced.arrange_reverse()

        row = reduced.reduce(element)
        return row.is_identity()


class PolyCyclicAutomorphismMap(AutomorphismMap):
    @singledispatchmethod
    def value(self, element: Any):
        raise TypeError(element)

    @value.register
    def _(self, element: GroupElement):
        return self._value(element)

    @value.register
    def _(self, element: Group):
        return element.represent.group([
            self._value(g)
            for g in element.generator
        ])

    def _value(self, element: GroupElement):
        reduced = PolyCyclicRowReduced()
        for k, v in self.group_element_map.items():
            reduced.append_mult(k, [v])

        result = reduced.reduce(element, [element.group.identity])
        for row in result.rows:
            return -row


class PolyCyclicGroupElement(GroupElement):
    group: PolyCyclicGroupRep
    power: list[int]

    def __hash__(self):
        return hash((id(self.group), tuple(self.power)))

    def __eq__(self, other):
        return self.group is other.group and self.power == other.power

    def __lt__(self, other):
        return self.power < other.power

    def _normalize_sequence(self, sequence):
        stack = []
        right_stack = list(sequence)
        right_stack.reverse()

        while right_stack:
            self._show(stack, right_stack)

            right = right_stack.pop()

            if right.power == 0:
                continue

            if right.power < 0:
                if right.index in self.group.power_relation:
                    right_stack.extend(
                        self._to_index(self.group.power_relation[right.index])
                    )
                self._append_index(
                    right_stack,
                    right.index, right.power + self.group.degree
                )
                continue

            if len(stack) == 0:
                stack.append(right)
                continue

            left = stack.pop()

            if left.index < right.index:
                stack.extend([left, right])
            elif left.index == right.index:
                q, r = divmod(left.power + right.power, self.group.degree)
                if left.index in self.group.power_relation:
                    for _ in range(q):
                        right_stack.extend(
                            self._to_index(
                                self.group.power_relation[left.index]
                            )
                        )
                self._append_index(right_stack,left.index, r)
            else:
                pair = left.index, right.index
                if pair not in self.group.commute_relation:
                    right_stack.extend([left, right])
                else:
                    self._append_index(
                        right_stack,
                        right.index, right.power - 1
                    )
                    for _ in range(left.power):
                        right_stack.extend(
                            self._to_index(
                                self.group.commute_relation[pair]
                            )
                        )
                        self._append_index(right_stack,left.index, 1)
                    self._append_index(right_stack,right.index, 1)

        self._show(stack, right_stack)

        # return result
        p = [0] * self.group.number
        for left in stack:
            p[left.index] = left.power
        return PolyCyclicGroupElement(group=self.group, power=p)

    @staticmethod
    def _append_index(stack, index, power):
        stack.append(PolyCyclicIndex(index=index, power=power))

    def __add__(self, other: 'PolyCyclicGroupElement'):
        return self._normalize_sequence(
            itertools.chain(
                self._build_stack(),
                other._build_stack()
            )
        )

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        stack = self._build_stack()
        stack.reverse()
        return self._normalize_sequence([
            PolyCyclicIndex(index=index.index, power=-index.power)
            for index in stack
        ])

    def __mul__(self, other):
        if other == 0:
            return self.group.identity

        current = self
        for i in range(1, other):
            current += self
        return current

    def __str__(self):
        return str(self.power)

    def max_index(self):
        index = None
        for i, p in enumerate(self.power):
            if p != 0:
                index = i
        return index

    def min_index(self):
        for i, p in enumerate(self.power):
            if p != 0:
                return i

    def to_index_list(self):
        result = []
        for i, p in enumerate(self.power):
            for _ in range(p):
                result.append(i)
        return result

    def is_identity(self) -> bool:
        for p in self.power:
            if p != 0:
                return False
        return True

    def order(self) -> int:
        current = self
        current_order = 1

        while not current.is_identity():
            current_order *= self.group.degree
            current *= self.group.degree

        return current_order

    def _build_stack(self):
        power_list = []
        for i, p in enumerate(self.power):
            if p != 0:
                power_list.append(PolyCyclicIndex(index=i, power=p))
        return power_list

    def _to_index(self, int_list):
        return [
            PolyCyclicIndex(index=index, power=1)
            for index in int_list[::-1]
        ]

    def _show(self, stack, right_stack):
        # print(stack)
        # print(right_stack)
        # input()
        pass


class PolyCyclicIndex(BaseModel):
    index: int
    power: int
