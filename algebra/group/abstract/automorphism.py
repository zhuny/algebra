import io

from algebra.group.abstract.base import GroupRep, Group, GroupElement


class AutomorphismGroupRep(GroupRep):
    structure: Group

    @property
    def group_cls(self):
        return AutomorphismGroup

    @property
    def element_cls(self):
        return AutomorphismGroupElement

    def element(self, element):
        return self.element_cls(group=self, group_element_map=element)


class AutomorphismGroup(Group):
    generator: list['AutomorphismGroupElement']


class AutomorphismGroupElement(GroupElement):
    group_element_map: dict[GroupElement, GroupElement]

    def __str__(self):
        with io.StringIO() as output:
            for k, v in self.group_element_map.items():
                print(k, '->', v, file=output)
            return output.getvalue().strip()

    @classmethod
    def from_value(cls, rep, v):
        if isinstance(v, dict):
            return cls(
                represent=rep,
                group_element_map=dict(v)
            )
        else:
            raise ValueError('Unknown Type')

    def act(self, o):
        assert False
