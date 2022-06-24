from dataclasses import dataclass

from algebra.group.abstract.base import GroupElement, GroupRep


@dataclass
class PolyCyclicGroupRep(GroupRep):
    pass


@dataclass
class PoLyCyclicGroupElement(GroupElement):
    group: PolyCyclicGroupRep
