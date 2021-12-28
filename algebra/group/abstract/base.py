from dataclasses import dataclass
from typing import List, TypeVar, Generic


@dataclass
class GroupRep:
    @property
    def identity(self):
        raise NotImplementedError


@dataclass
class Group:
    group: GroupRep
    generator: List['GroupElement']

    def random_element(self):
        raise NotImplementedError

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


T = TypeVar("T")


@dataclass
class GroupElement(Generic[T]):
    group: GroupRep

    def __add__(self, other):
        raise NotImplementedError

    def __neg__(self):
        raise NotImplementedError

    def act(self, o: T) -> T:
        # raise NotImplementedError
        """
        "Group Action" on some Set and T is a element of the set.

        :param o: Element on T
        :return: Another T
        """
        pass
