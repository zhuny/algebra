from algebra.group.abstract.set_action import MonomialActionGroupRep
from algebra.ring.polynomial.base import PolynomialRing
from algebra.ring.polynomial.naming import (VariableNameIndexGenerator, VariableNameListGenerator)
from algebra.ring.polynomial.variable import CombineVariableSystem


class GaloisGroupConstructor:
    def __init__(self, polynomial):
        self.polynomial = polynomial

    def run(self):
        degree = self.polynomial.degree()
        v_system = CombineVariableSystem([
            VariableNameIndexGenerator('x', degree),
            VariableNameListGenerator('X')
        ])

        pr = PolynomialRing(
            self.polynomial.ring.field,
            variable_system=v_system
        )
        ideal = self._build_ideal(pr)

        x = pr.variable.x
        v_group = MonomialActionGroupRep(x).as_group()
        total = self._build_resolvent(
            pr, v_group,
            x[0] * x[2] + x[1] * x[3]
        )

        print(total)

        print('Result =', total % ideal)

    def _build_ideal(self, pr):
        v_list = pr.variable.x
        xx = pr.variable.X

        total = pr.element([1])
        for v in v_list:
            total *= xx - v

        generator_list = []
        for i in range(self.polynomial.degree()):
            total, xx_coeff = divmod(total, xx)
            generator_list.append(xx_coeff - self.polynomial[i])

        return pr.ideal(generator_list)

    def _build_resolvent(self, pr, v_group, x):
        answer = pr.element([1])
        orbit = []

        for g in v_group.element_list():
            gx = g.act_polynomial(x)
            if gx not in orbit:
                answer *= pr.variable.X - gx
                orbit.append(gx)

        return answer
