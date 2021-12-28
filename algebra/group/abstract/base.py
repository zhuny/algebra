from dataclasses import dataclass
from typing import List


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


@dataclass
class GroupElement:
    group: GroupRep

    def __add__(self, other):
        raise NotImplementedError

    def __neg__(self):
        raise NotImplementedError
