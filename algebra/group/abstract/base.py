from dataclasses import dataclass, field
from queue import Queue
from typing import List, TypeVar, Generic, Set, Dict, Optional, Iterator

T = TypeVar("T")


@dataclass
class GroupRep:
    @property
    def identity(self):
        raise NotImplementedError

    def object_list(self):
        raise NotImplementedError

    def element(self, *args):
        raise NotImplementedError

    def group(self, *elements):
        for element in elements:
            if not isinstance(element, GroupElement):
                raise TypeError("GroupElement should be given")

            if element.group != self:
                raise ValueError("Element should be belong to this group")

        return Group(represent=self, generator=list(elements))

    def group_(self, elements):
        """
        self.group_([
            [[0, 1, 2, 3]],
            [[0, 2], [1, 3]]
        ])
        :param elements:
        :return:
        """
        ol = list(self.object_list())
        generator_list = []
        for element in elements:
            rep_elem = [
                [ol[i] for i in chain]
                for chain in element
            ]
            generator_list.append(self.element(*rep_elem))
        return self.group(*generator_list)


class StabilizerTraveler:
    def __init__(self, group):
        self.group: Group = group

    def visit(self):
        stack = [(
            self.group.stabilizer_chain(),
            self.group.represent.identity
        )]

        while stack:
            chain, element = stack.pop()
            chain: StabilizerChain
            element: GroupElement
            if chain.is_trivial():
                yield element
            else:
                for t in chain.transversal.values():
                    stack.append((
                        chain.stabilizer,
                        element + t
                    ))


@dataclass
class Group(Generic[T]):
    represent: GroupRep
    generator: List['GroupElement']
    _stabilizer_chain: Optional['StabilizerChain'] = None

    def copy(self):
        return self.represent.group(*self.generator)

    def order(self):
        return self.stabilizer_chain().order

    def object_list(self) -> List[T]:
        raise NotImplementedError

    def element_list(self) -> Iterator['GroupElement']:
        return StabilizerTraveler(self).visit()

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

    def stabilizer(self, o: T) -> 'Group':
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
            generator=new_generator
        )

    def stabilizer_chain(self) -> 'StabilizerChain':
        if self._stabilizer_chain is not None:
            return self._stabilizer_chain

        chain = StabilizerChain(group=self.represent.group())
        obj_iter = ElementContainer(self.represent.object_list())
        for g in self.generator:
            chain.extend(g, obj_iter)
        self._stabilizer_chain = chain
        return chain

    def element_test(self, element: 'GroupElement'):
        return self.stabilizer_chain().element_test(element)

    def normal_closure(self, element_list: List['GroupElement']):
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

    def center(self):
        chain = StabilizerChain(group=self.represent.group())
        obj_iter = ElementContainer(self.represent.object_list())

        for element in self.element_list():
            if self.is_commute(element):
                if not chain.element_test(element):
                    chain.extend(element, obj_iter)

        return chain.construct()

    def is_commute(self, element: 'GroupElement'):
        for gen in self.generator:
            left = gen + element
            right = element + gen
            if left != right:
                return False
        return True

    def is_trivial(self):
        for gen in self.generator:
            if not gen.is_identity():
                return False
        return True

    def is_normal(self, subgroup: 'Group'):
        for sub_gen in subgroup.generator:
            for gen in self.generator:
                conjugate = gen + sub_gen - gen
                if not subgroup.element_test(conjugate):
                    return False
        return True

    def centralizer(self, element: 'GroupElement'):
        pass

    def normalizer(self, subgroup: 'Group'):
        pass

    def conjugacy_classes(self):
        pass

    def conjugacy_classes_subgroups(self):
        pass

    def intermediate_subgroups(self):
        pass

    def normal_subgroups(self):
        pass

    def maximal_subgroup_class_reps(self):
        pass

    def isomorphism_groups(self, others: 'Group'):
        pass

    def g_quotients(self, others: 'Group'):
        pass


class ElementContainer:
    def __init__(self, element_list):
        self.element_set = set(element_list)
        self.element_iter = self.iter_repeat()
        self.element_used = set()

    def iter_repeat(self):
        while True:
            for element in self.element_set:
                yield element

    def get_next(self, group_element: 'GroupElement'):
        for element in self.element_iter:
            if element in self.element_used:
                continue
            acted_element = group_element.act(element)
            if acted_element != element:
                self.element_used.add(element)
                return element


@dataclass
class StabilizerChain(Generic[T]):
    group: Group
    point: T = None
    transversal: Dict[T, 'GroupElement'] = field(default_factory=dict)
    stabilizer: Optional['StabilizerChain'] = None
    depth: int = 0

    @property
    def order(self):
        if self.is_trivial():
            return 1
        else:
            return len(self.transversal) * self.stabilizer.order

    def is_trivial(self):
        return self.point is None

    def travel(self):
        current = self
        yield current
        while not current.is_trivial():
            current = current.stabilizer
            yield current

    def element_test(self, element: 'GroupElement'):
        if element.is_identity():
            return True

        for stabilizer in self.travel():
            if stabilizer.point is None:
                return element.is_identity()

            base = element.act(stabilizer.point)
            if base not in stabilizer.transversal:
                return False

            t = stabilizer.transversal[base]
            element -= t
            # TODO : representation may be needed

        # Unreachable
        return True

    def show(self):
        for stack in self.travel():
            print(f"=== STACK-{stack.depth} ===")
            print(f"Fixed Point : {stack.point}")
            print("Transversal")
            for k, t in stack.transversal.items():
                print(f"  - {k} : {t}")
            print("Group Generator")
            for g in stack.group.generator:
                print(f"  - {g}")
            print()

    def extend(self, alpha: 'GroupElement', next_object: ElementContainer):
        # It is implementation of Schreier-Sims algorithm
        if not self.element_test(alpha):  # Extend existing stabilizer chain
            if self.is_trivial():  # we are on the bottom of the chain
                # pick random object from base point
                beta = self.point = next_object.get_next(alpha)
                self.stabilizer = StabilizerChain(  # Add a new layer
                    group=self.group.represent.group(),
                    depth=self.depth + 1
                )
                self.group.generator.append(alpha)
                self.transversal[beta] = self.group.represent.identity
                delta = alpha.act(beta)
                s = alpha  # orbit algorithm for single generator group
                while delta != beta:
                    self.transversal[delta] = s
                    delta, s = alpha.act(delta), s + alpha
                self.stabilizer.extend(s, next_object)  # remove recursive
            else:
                queue = Queue()
                for delta, transversal in self.transversal.items():
                    queue.put((delta, transversal, False))

                while queue.qsize() > 0:
                    delta, transversal, is_new = queue.get()
                    check_element = [alpha]
                    if is_new:
                        check_element.extend(self.group.generator)

                    for element in check_element:
                        gamma = element.act(delta)
                        if gamma not in self.transversal:
                            new_element = transversal + element
                            self.transversal[gamma] = new_element
                            queue.put((gamma, new_element, True))
                        else:
                            self.stabilizer.extend(
                                transversal + element -
                                self.transversal[gamma],
                                next_object
                            )

                self.group.generator.append(alpha)

    def construct(self):
        new_group = self.group.copy()
        new_group._stabilizer_chain = self
        return new_group


@dataclass
class GroupElement(Generic[T]):
    group: GroupRep

    def __add__(self, other: 'GroupElement') -> 'GroupElement':
        raise NotImplementedError

    def __neg__(self) -> 'GroupElement':
        raise NotImplementedError

    def __sub__(self, other: 'GroupElement') -> 'GroupElement':
        return self + (-other)

    def is_identity(self) -> bool:
        raise NotImplementedError

    def order(self) -> int:
        raise NotImplementedError

    def act(self, o: T) -> T:
        # raise NotImplementedError
        """
        "Group Action" on some Set and T is a element of the set.

        :param o: Element on T
        :return: Another T
        """
        pass
