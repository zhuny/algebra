import collections

from algebra.group.abstract.base import Group


class MyQueue:
    def __init__(self):
        self.done = set()
        self.queued = set()

    def put(self, e):
        if e not in self.done:
            self.queued.add(e)

    def get(self):
        e = self.queued.pop()
        self.done.add(e)
        return e

    def qsize(self):
        return len(self.queued)


class DisjointSet:
    # 아마 util 어디로 이동될 듯
    def __init__(self, element_list):
        self._parent = {e: e for e in element_list}

    def connect(self, e1, e2):
        self._set_root(e1, self.root(e2))

    def is_connect(self, e1, e2):
        return self.root(e1) == self.root(e2)

    def root(self, e):
        while not self._is_root(e):
            e = self._parent[e]
        return e

    def _is_root(self, e):
        return e == self._parent[e]

    def _set_root(self, seed, target):
        if seed == target:
            return

        self._parent[seed] = target
        while self._is_root(seed):
            seed = self._parent[seed]
            self._parent[seed] = target

    def as_list(self):
        root_collect = collections.defaultdict(list)
        for e in self._parent:
            root_collect[self.root(e)].append(e)
        for v in root_collect.values():
            v.sort()
        return list(root_collect.values())


class FinestBlockSystem:
    def __init__(self, group):
        self.group: Group = group

    def _with_first_pair(self, iter_):
        the_first = None
        for i in iter_:
            if the_first is None:
                the_first = i
            else:
                yield the_first, i

    def calculate(self):
        min_system_size = 0
        finest_block_system = None

        # calculate finest block system for each seed
        ol = self.group.represent.object_list()
        for pair in self._with_first_pair(ol):
            block_system = self._block_system_with_seed(pair)
            if min_system_size < len(block_system):
                min_system_size = len(block_system)
                finest_block_system = block_system

        return finest_block_system

    def _block_system_with_seed(self, seed_set):
        ds = DisjointSet(self.group.represent.object_list())
        queue = MyQueue()

        for one, other in self._with_first_pair(seed_set):
            ds.connect(one, other)
            queue.put(one)
            queue.put(other)

        while queue.qsize() > 0:
            e1 = queue.get()
            e2 = ds.root(e1)

            if e1 == e2:
                continue

            for g in self.group.generator:
                a1 = g.act(e1)
                a2 = g.act(e2)

                if not ds.is_connect(a1, a2):
                    ds.connect(a1, a2)
                    queue.put(a1)
                    queue.put(a2)

        return ds.as_list()
