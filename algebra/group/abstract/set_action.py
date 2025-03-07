from pydantic import BaseModel
from typing import Any

from algebra.group.abstract.permutation import PermutationGroupRep, \
    PermutationGroupElement, PermutationObject


class MonomialActionGroupRep(PermutationGroupRep):
    custom_object_list: list[Any]
    degree: int = 0

    def model_post_init(self, __context: Any) -> None:
        self.degree = len(self.custom_object_list)

    def __hash__(self):
        # super class가 hash가 정의 되어 있음에도 실행을 안한다.
        return id(self)

    @property
    def cls_element(self):
        return MonomialActionGroupElement


class MonomialActionGroupElement(PermutationGroupElement):
    def act_polynomial(self, polynomial):
        from algebra.ring.polynomial.base import Monomial, PolynomialRingElement

        polynomial_map = {}

        for o, value in polynomial.value.items():
            o: Monomial
            new_power = list(o.power)
            for k, v in self.perm_map.items():
                new_power[v.value] = o.power[k.value]
            new_monomial = Monomial(power=new_power, ring=o.ring)
            polynomial_map[new_monomial] = value

        return PolynomialRingElement(value=polynomial_map, ring=polynomial.ring)

    def __hash__(self):
        return hash((self.group, str(self)))
