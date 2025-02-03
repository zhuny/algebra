import dataclasses
import itertools
from dataclasses import dataclass

from algebra.group.abstract.automorphism import AutomorphismGroupRep
from algebra.group.abstract.base import GroupElement, GroupRep, Group


@dataclass
class PolyCyclicGroupRep(GroupRep):
    degree: int
    number: int
    power_relation: dict[int, list[int]] = dataclasses.field(
        default_factory=dict
    )
    commute_relation: dict[tuple[int, int], list[int]] = dataclasses.field(
        default_factory=dict
    )

    @property
    def group_cls(self):
        return PolyCyclicGroup

    def element(self, power):
        return PolyCyclicGroupElement(self, power)

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


@dataclass
class PolyCyclicGroup(Group):
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

    def lower_exponent_p_central(self, other: 'PolyCyclicGroup'):
        result = PolyCyclicGroup(represent=self.represent, generator=[])

        for g1 in self.generator:
            for h in other.generator:
                for g2 in other.generator:
                    result._append(
                        g1 + h - g1 - h +
                        g2 * self.represent.degree
                    )

        return result

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

        return auto_group_rep.group(auto_group_gen)

    def order(self):
        return pow(self.represent.degree, len(self.generator))

    def p_multiplicator(self):
        return self.lower_exponent_p_central(self)

    def show(self, msg=None):
        rep: PolyCyclicGroupRep = self.represent
        if msg:
            print(msg)
        print(f'PCG({rep.degree}, {rep.number}) with..')
        for i, rel in rep.power_relation.items():
            print(i, rel)
        for (j, i), rel in rep.commute_relation.items():
            print(j, i, rel)
        print()

    def _append(self, element: 'PolyCyclicGroupElement'):
        element = element.normalize()
        index_map = {
            g.min_index(): g
            for g in self.generator
        }

        while not element.is_identity():
            min_index = element.min_index()
            if min_index in index_map:
                element -= index_map[min_index]
                element = element.normalize()
            else:
                self.generator.append(element)
                break


@dataclass
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
                right_stack.append(
                    PolyCyclicIndex(
                        right.index,
                        right.power + self.group.degree
                    )
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
                right_stack.append(PolyCyclicIndex(left.index, r))
            else:
                pair = left.index, right.index
                if pair not in self.group.commute_relation:
                    right_stack.extend([left, right])
                else:
                    right_stack.append(PolyCyclicIndex(right.index, right.power - 1))
                    for _ in range(left.power):
                        right_stack.extend(
                            self._to_index(
                                self.group.commute_relation[pair]
                            )
                        )
                        right_stack.append(PolyCyclicIndex(left.index, 1))
                    right_stack.append(PolyCyclicIndex(right.index, 1))

        self._show(stack, right_stack)

        # return result
        p = [0] * self.group.number
        for left in stack:
            p[left.index] = left.power
        return PolyCyclicGroupElement(group=self.group, power=p)

    def __add__(self, other: 'PolyCyclicElement'):
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
            PolyCyclicIndex(index.index, -index.power)
            for index in stack
        ])

    def __mul__(self, other):
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

    def normalize(self):
        for i, p in enumerate(self.power):
            if p != 0:
                e = pow(abs(p), self.group.degree - 2, self.group.degree)
                if p < 0:
                    e = -e
                return self * e
        return self

    def _build_stack(self):
        power_list = []
        for i, p in enumerate(self.power):
            if p != 0:
                power_list.append(PolyCyclicIndex(i, p))
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


@dataclass
class PolyCyclicIndex:
    index: int
    power: int
