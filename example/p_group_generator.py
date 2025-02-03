import dataclasses
import itertools
from dataclasses import dataclass


@dataclass
class PolyCyclicGroup:
    degree: int
    number: int
    power_relation: dict[int, list[int]] = dataclasses.field(default_factory=dict)
    commute_relation: dict[tuple[int, int], list[int]] = dataclasses.field(
        default_factory=dict
    )

    def add_number(self):
        n = self.number
        self.number += 1
        return n

    def identity(self):
        return PolyCyclicElement(self, [0] * self.number)

    def generator(self, index):
        power = [0] * self.number
        power[index] = 1
        return PolyCyclicElement(self, power)

    def generator_list(self, count=1):
        gen_list = [self.generator(i) for i in range(count)]
        if count == 1:
            return gen_list
        return itertools.combinations(gen_list, count)

    def p_covering_group(self):
        # gen
        result = PolyCyclicGroup(degree=self.degree, number=self.number)

        for i in range(self.number):
            new_i = result.add_number()
            result.power_relation[i] = self.power_relation.get(i, []) + [new_i]

        for i in range(self.number):
            for j in range(i):
                p = i, j
                new_p = result.add_number()
                result.commute_relation[p] = (
                    self.commute_relation.get(p, []) + [new_p]
                )

        result._optimize()
        result._show('Normalized')
        return result

    def _optimize(self):
        while self._optimize_once():
            pass

    def _optimize_once(self):
        # optimize
        for left, right in self._optimize_check():
            if left != right:
                diff = left - right
                if diff.is_zero():
                    diff = - left + right
                diff_index = diff.max_index()
                left = diff - self.generator(diff_index)
                self._remove_gen(diff_index, left)
                return True

        return False

    def _optimize_check(self):
        for ei in self.generator_list():
            ei_p = ei * (self.degree - 1)

            yield (ei + ei_p) + ei, ei + (ei_p + ei)

        for ei, ej in self.generator_list(2):
            ei_p = ei * (self.degree - 1)
            ej_p = ej * (self.degree - 1)

            yield (ej_p + ej) + ei, ej_p + (ej + ei)
            yield (ej + ei) + ei_p, ej + (ei + ei_p)

        for ei, ej, ek in self.generator_list(3):
            yield (ek + ej) + ei, ek + (ej + ei)

    def _remove_gen(self, diff_index, index_rel):
        new_power_relation = self._convert_relation(self.power_relation, diff_index, index_rel)
        new_commute_relation = self._convert_relation(self.commute_relation, diff_index, index_rel)
        self._update_dict(self.power_relation, new_power_relation)
        self._update_dict(self.commute_relation, new_commute_relation)

        self.number -= 1

    def _convert_relation(self, relation, diff_index, index_rel):
        return {
            key: self._convert_index(rel, diff_index, index_rel)
            for key, rel in relation.items()
        }

    def _convert_index(self, rel, diff_index, index_rel):
        if diff_index in rel:
            new_rel = self.identity()
            for index in rel:
                if index == diff_index:
                    new_rel += index_rel
                else:
                    new_rel += self.generator(index)
            rel = new_rel.to_index_list()

        return [
            i if i < diff_index else i - 1
            for i in rel
        ]

    def _update_dict(self, relation, new_relation):
        relation.clear()
        for k, v in new_relation.items():
            if v:
                relation[k] = v

    def _show(self, msg=None):
        if msg:
            print(msg)
        for i, rel in self.power_relation.items():
            print(i, rel)
        for (j, i), rel in self.commute_relation.items():
            print(j, i, rel)
        print()


@dataclass(unsafe_hash=False, eq=False)
class PolyCyclicElement:
    group: PolyCyclicGroup
    power: list[int]

    def __hash__(self):
        return hash((id(self.group), tuple(self.power)))

    def __eq__(self, other):
        return self.power == other.power

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
        return PolyCyclicElement(group=self.group, power=p)

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
            if p > 0:
                index = i
        return index

    def to_index_list(self):
        result = []
        for i, p in enumerate(self.power):
            for _ in range(p):
                result.append(i)
        return result

    def is_zero(self):
        for p in self.power:
            if p != 0:
                return False
        return True

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


def main():
    # D8
    g = PolyCyclicGroup(2, 3)
    g.commute_relation[1, 0] = [2]
    g.power_relation[1] = [2]

    g.p_covering_group()


if __name__ == '__main__':
    main()
