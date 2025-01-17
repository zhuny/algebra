import collections
import sys

from algebra.group.abstract.permutation import PermutationGroupRep
from algebra.group.abstract.shortcut import symmetric_group


class Node:
    def __init__(self, value):
        self.value = value
        self.upper = set()
        self.lower = set()

    def is_upper(self, other: 'Node'):
        return self.compare(other.value, self.value)

    def is_lower(self, other: 'Node'):
        return self.compare(self.value, other.value)

    def compare(self, left, right):
        assert False, "Not Implementation Error"

    def link(self, other: 'Node'):
        self.upper.add(other)
        other.lower.add(self)

    def unlink(self, other: 'Node'):
        self.upper.discard(other)
        other.lower.discard(self)

    def string(self):
        return self.value


class TopNode(Node):
    def __init__(self):
        super().__init__('Top')

    def is_upper(self, other: 'Node'):
        return True

    def is_lower(self, other: 'Node'):
        return isinstance(other, TopNode)


class BottomNode(Node):
    def __init__(self):
        super().__init__('Bottom')

    def is_upper(self, other: 'Node'):
        return isinstance(other, BottomNode)

    def is_lower(self, other: 'Node'):
        return True


class PosetOrder:
    def __init__(self, node_cls):
        self.top = TopNode()
        self.bottom = BottomNode()
        self.bottom.link(self.top)

        self.node_cls = node_cls
        self.size = 0

    def insert(self, element):
        element_node = self.node_cls(element)
        lower_list = self._get_lower(element_node)
        upper_list = self._get_upper(element_node)

        if len(lower_list) == 1 and len(upper_list) == 1:
            if lower_list == upper_list:
                # 이미 있는 경우
                return

        self.size += 1

        for lower in lower_list:
            for upper in upper_list:
                lower.unlink(upper)

        for lower in lower_list:
            lower.link(element_node)
        for upper in upper_list:
            element_node.link(upper)

    def show(self):
        for element in self.travel():
            for upper in element.upper:
                print(element.string(), '->', upper.string())
        print(self.size, 'elements')

    def travel(self):
        stack = {self.bottom}
        done = set()

        while stack:
            element = stack.pop()
            if element in done:
                continue
            yield element
            done.add(element)
            stack.update(element.upper)

    def element_list(self):
        for element in list(self.travel()):
            if element == self.top:
                continue
            if element == self.bottom:
                continue
            yield element.value

    def _get_lower(self, element):
        stack = {self.bottom}
        done = set()

        while stack:
            current = stack.pop()
            next_list = [
                n
                for n in current.upper
                if n.is_lower(element)
            ]
            if len(next_list) == 0:
                done.add(current)
            else:
                stack.update(next_list)

        return done

    def _get_upper(self, element):
        stack = {self.top}
        done = set()

        while stack:
            current = stack.pop()
            next_list = [
                n
                for n in current.lower
                if n.is_upper(element)
            ]
            if len(next_list) == 0:
                done.add(current)
            else:
                stack.update(next_list)

        return done


class IntegerNode(Node):
    def is_upper(self, other: 'IntegerNode'):
        return self.value % other.value == 0

    def is_lower(self, other: 'IntegerNode'):
        return other.value % self.value == 0


class GroupNode(Node):
    def compare(self, left, right):
        return left.is_subgroup(right)


class GroupSetNode(Node):
    def compare(self, left, right):
        for lg in left:
            for rg in right:
                if lg.is_subgroup(rg):
                    return True
        return False

    def string(self):
        for g in self.value:
            return f"{g}, {g.order()}"


class GroupingGroup:
    def __init__(self, check_name, condition=None):
        self.check_name = check_name
        self.group_by = []
        self.condition = condition

    def append(self, g):
        if self.condition is not None:
            if not getattr(g, self.condition)():
                return

        for item in self.group_by:
            if getattr(item[0], self.check_name)(g):
                item[1].append(g)
                return

        self.group_by.append((g, [g]))

    def show(self):
        if self.condition is None:
            print(self.check_name)
        else:
            print(self.check_name, 'with', self.condition)

        for g, g_list in self.group_by:
            print(g, g.order(), len(g_list))
        print(len(self.group_by), 'grouping')
        print()

    def get_grouping(self):
        for g, count in self.group_by:
            yield count


def main():
    po = PosetOrder(GroupNode)
    s_n = symmetric_group(int(sys.argv[1]))

    po.insert(s_n.represent.group())

    for i, element in enumerate(s_n.element_list()):
        for group in po.element_list():
            po.insert(group.append(element))

        print(i, element)
    print()

    grouping_dict = {
        'iso': GroupingGroup('is_isomorphism'),
        'con': GroupingGroup('is_conjugate'),
        'galois': GroupingGroup('is_isomorphism', condition='is_transitive')
    }
    for group in po.element_list():
        for grouping in grouping_dict.values():
            grouping.append(group)

    for grouping in grouping_dict.values():
        grouping.show()

    po2 = PosetOrder(GroupSetNode)
    for group_set in grouping_dict['galois'].get_grouping():
        po2.insert(group_set)
    po2.show()


if __name__ == '__main__':
    main()
