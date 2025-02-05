import io

from pydantic import BaseModel

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
        return self.element_cls(group=self, value=element)


class AutomorphismGroup(Group):
    generator: list['AutomorphismGroupElement']


class AutomorphismMap(BaseModel):
    group_element_map: dict[GroupElement, GroupElement]

    def value(self, element: GroupElement):
        raise NotImplementedError(self)


class AutomorphismGroupElement(GroupElement):
    value: AutomorphismMap

    def __str__(self):
        with io.StringIO() as output:
            for k, v in self.value.group_element_map.items():
                print(k, '->', v, file=output)
            return output.getvalue().strip()

    def act(self, o):
        return self.value.value(o)
