from dataclasses import dataclass
from typing import List


@dataclass
class Group:
    @property
    def identity(self):
        raise NotImplementedError


@dataclass
class Subgroup:
    group: Group
    generator: List['GroupElement']

    def random_element(self):
        raise NotImplementedError

    def centralizer(self, element: 'GroupElement'):
        pass

    def normalizer(self, subgroup: 'Subgroup'):
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

    def isomorphism_groups(self, others: 'Subgroup'):
        pass

    def g_quotients(self, others: 'Subgroup'):
        pass


@dataclass
class GroupElement:
    group: Group


@dataclass
class PermutationGroup(Group):
    pass


@dataclass
class PermutationGroupElement(GroupElement):
    group: PermutationGroup


@dataclass
class PolyCyclicGroup(Group):
    pass


@dataclass
class PoLyCyclicGroupElement(GroupElement):
    group: PolyCyclicGroup
