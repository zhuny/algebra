from dataclasses import dataclass
from typing import List, TypeVar, Generic, Set

T = TypeVar("T")


@dataclass
class GroupRep:
    @property
    def identity(self):
        raise NotImplementedError

    def group(self, *elements):
        return Group(represent=self, generator=list(elements))


@dataclass
class Group(Generic[T]):
    represent: GroupRep
    generator: List['GroupElement']

    def random_element(self):
        raise NotImplementedError

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


@dataclass
class GroupElement(Generic[T]):
    group: GroupRep

    def __add__(self, other: 'GroupElement') -> 'GroupElement':
        raise NotImplementedError

    def __neg__(self) -> 'GroupElement':
        raise NotImplementedError

    def __sub__(self, other: 'GroupElement') -> 'GroupElement':
        return self + (-other)

    def act(self, o: T) -> T:
        # raise NotImplementedError
        """
        "Group Action" on some Set and T is a element of the set.

        :param o: Element on T
        :return: Another T
        """
        pass
