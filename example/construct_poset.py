import argparse
import collections
import json
import secrets
import sys
from pathlib import Path

import tqdm

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

    def dump(self):
        return {
            'type': type(self).__name__,
            'value': self.to_json()
        }

    @classmethod
    def load(cls, info, context):
        if info['type'] != cls.__name__:
            return

        return cls(value=cls.from_json(info['value'], context))

    def to_json(self):
        return self.value

    @classmethod
    def from_json(cls, value, context):
        return value


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

    def has(self, element):
        element_node = self.node_cls(element)
        lower_list = self._get_lower(element_node)
        upper_list = self._get_upper(element_node)

        if len(lower_list) == 1 and len(upper_list) == 1:
            if lower_list == upper_list:
                # 이미 있는 경우
                return True

        return False

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

    def dump(self, filename):
        if filename is None:
            return

        node_to_id = {}
        id_to_node = {}
        for element in self.travel():
            token = secrets.token_hex(8)
            node_to_id[element] = token
            id_to_node[token] = element.dump()

        relation = [
            [node_to_id[element], node_to_id[upper]]
            for element in self.travel()
            for upper in element.upper
        ]

        info = {
            'node_list': [
                {'key': key, 'value': value}
                for key, value in id_to_node.items()
            ],
            'relation': relation
        }

        with open(filename, 'w') as f:
            f.write(json.dumps(info))

    def load(self, filename, context):
        with open(filename, 'r') as f:
            info = json.loads(f.read())

        id_to_node = {}
        for element in info['node_list']:
            element_value = element['value']
            if element_value['type'] == 'TopNode':
                node = self.top
            elif element_value['type'] == 'BottomNode':
                node = self.bottom
            else:
                node = self.node_cls.load(element_value, context)
            id_to_node[element['key']] = node

        self.bottom.unlink(self.top)
        self.size = len(id_to_node) - 2

        for lower, upper in info['relation']:
            lower_node = id_to_node[lower]
            upper_node = id_to_node[upper]
            lower_node.link(upper_node)

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

    def to_json(self):
        return [
            list(g.to_seq())
            for g in self.value.generator
        ]

    @classmethod
    def from_json(cls, value, context):
        from algebra.group.abstract.base import Group
        group: Group = context['group']
        return group.represent.group_(value)


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
            if getattr(item[2], self.check_name)(g):
                item[3].append(g)
                return

        self.group_by.append((g.order(), len(self.group_by), g, [g]))

    def show(self):
        if self.condition is None:
            print(self.check_name)
        else:
            print(self.check_name, 'with', self.condition)

        self.group_by.sort()
        for o, _, g, g_list in self.group_by:
            print(g, o, len(g_list))
        print(len(self.group_by), 'grouping')
        print()

    def get_grouping(self):
        for _, _, _, grouping in self.group_by:
            yield grouping


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('degree', type=int)
    parser.add_argument('-c', default=None, help='Cache file', dest='cache')

    return parser.parse_args()


def factorial(n):
    answer = 1
    for i in range(2, n+1):
        answer *= i
    return answer


def main():
    args = parse_args()

    po = PosetOrder(GroupNode)
    s_n = symmetric_group(args.degree)

    context = {'group': s_n}

    if args.cache:
        if Path(args.cache).exists():
            po.load(args.cache, context)
            po.show()

    build_subgroup(po, s_n, args)
    show_subgroup_key(po, s_n, args)


def show_subgroup_key(po, s_n, args):
    key_set = set()
    for group in po.element_list():
        print(group, group.group_id())
        key_set.add(group.group_id())

    print(len(key_set))


def build_subgroup(po, s_n, args):
    po.insert(s_n.represent.group())
    count = 0

    for element in tqdm.tqdm(s_n.element_list(), total=factorial(args.degree)):
        if po.has(s_n.represent.group(element)):
            continue

        count += 1

        for group in po.element_list():
            po.insert(group.append(element))

        if count % 10 == 0:
            po.dump(args.cache)

    print(po.size)
    po.dump(args.cache)
    print()

    grouping_dict = {
        'iso': GroupingGroup('is_isomorphism'),
        'con': GroupingGroup('is_conjugate'),
        'galois': GroupingGroup('is_conjugate', condition='is_transitive')
    }

    for group in tqdm.tqdm(po.element_list(), total=po.size):
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
