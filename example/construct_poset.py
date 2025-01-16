import collections

from algebra.group.abstract.permutation import PermutationGroupRep
from algebra.group.abstract.shortcut import symmetric_group


class Node:
    def __init__(self, value):
        self.value = value
        self.upper = set()
        self.lower = set()

    def is_upper(self, other: 'Node'):
        raise NotImplementedError(self)

    def is_lower(self, other: 'Node'):
        raise NotImplementedError(self)

    def link(self, other: 'Node'):
        self.upper.add(other)
        other.lower.add(self)

    def unlink(self, other: 'Node'):
        self.upper.discard(other)
        other.lower.discard(self)


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
                print(element.value, '->', upper.value)
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
    def is_upper(self, other: 'GroupNode'):
        return self.compare(self.value, other.value)

    def is_lower(self, other: 'GroupNode'):
        return self.compare(other.value, self.value)

    @staticmethod
    def compare(left, right):
        return right.is_subgroup(left)


def get_isomorphism(group_list, new_group):
    for group in group_list:
        if group[0].is_isomorphism(new_group):
            return group


def main():
    po = PosetOrder(GroupNode)
    s_n = symmetric_group(4)

    po.insert(s_n.represent.group())

    for i, element in enumerate(s_n.element_list()):
        for group in po.element_list():
            po.insert(group.append(element))

        print(i, element)

    up_iso = []
    for group in po.element_list():
        if group.is_transitive():
            auto = get_isomorphism(up_iso, group)
            if auto is None:
                up_iso.append([group, 1])
            else:
                auto[1] += 1

    print(len(up_iso))
    for group, count in up_iso:
        print(group, group.order())


if __name__ == '__main__':
    main()
