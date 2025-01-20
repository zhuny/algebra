import dataclasses
import itertools
from dataclasses import dataclass


@dataclass
class PolyCyclicGroup:
    degree: int
    number: int
    power_relation: dict = dataclasses.field(default_factory=dict)
    commute_relation: dict = dataclasses.field(default_factory=dict)

    def add_number(self):
        n = self.number
        self.number += 1
        return n

    def generator(self, index):
        power = [0] * self.number
        power[index] = 1
        return PolyCyclicElement(self, power)

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

        # optimize
        for new_i in range(self.number, result.number):
            e = result.generator(new_i)
            ep = e * (self.degree - 1)
            left = (e + ep) + e
            right = e + (ep + e)
            print(left, right)
            input()


@dataclass(unsafe_hash=False, eq=False)
class PolyCyclicElement:
    group: PolyCyclicGroup
    power: list[int]

    def __hash__(self):
        return hash((id(self.group), tuple(self.power)))

    def __eq__(self, other):
        return self.power == other.power

    def __add__(self, other: 'PolyCyclicElement'):
        # print(self.power, other.power)

        stack = self._build_stack()
        right_stack = other._build_stack()
        right_stack.reverse()

        while right_stack:
            self._show(stack, right_stack)

            if right_stack[-1].power == 0:
                right_stack.pop()
                continue

            if len(stack) == 0:
                stack.append(right_stack.pop())
                continue

            left = stack.pop()
            right = right_stack.pop()

            if left.index < right.index:
                stack.extend([left, right])
            elif left.index == right.index:
                q, r = divmod(left.power + right.power, self.group.degree)
                if left.index in self.group.power_relation:
                    for _ in range(q):
                        right_stack.extend(self.group.power_relation[left.index])
                right_stack.append(PolyCyclicIndex(left.index, r))
            else:
                pair = left.index, right.index
                if pair not in self.group.commute_relation:
                    right_stack.extend([left, right])
                else:
                    right_stack.append(PolyCyclicIndex(right.index, right.power - 1))
                    for _ in range(left.power):
                        right_stack.extend(self.group.commute_relation[pair])
                        right_stack.append(PolyCyclicIndex(left.index, 1))
                    right_stack.append(PolyCyclicIndex(right.index, 1))

        self._show(stack, right_stack)

        # return result
        p = [0] * self.group.number
        for left in stack:
            p[left.index] = left.power
        return PolyCyclicElement(group=self.group, power=p)

    def __mul__(self, other):
        current = self
        for i in range(1, other):
            current += self
        return current

    def __str__(self):
        return str(self.power)

    def _build_stack(self):
        power_list = []
        for i, p in enumerate(self.power):
            if p > 0:
                power_list.append(PolyCyclicIndex(i, p))
        return power_list

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
    # g = PGroup(degree=2, number=5)
    # g.power_relation[0] = 3
    # g.power_relation[1] = 2
    # g.power_relation[2] = 4
    # g.power_relation[3] = 4
    # g.commute_relation[1, 0] = 2
    # g.commute_relation[2, 0] = 4
    #
    # g.build_weight()

    g = PolyCyclicGroup(2, 3)
    g.commute_relation[1, 0] = [2]
    g.power_relation[1] = [2]

    g.p_covering_group()


if __name__ == '__main__':
    main()
