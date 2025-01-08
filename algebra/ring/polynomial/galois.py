from algebra.group.abstract.base import GroupRep
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
        v_group = GroupRep(x).as_group()
        total = self._build_resolvent(
            pr, v_group,
            x[0] * x[2] + x[1] * x[3]
        )

        print(total)

        print(total % ideal)

    def _build_ideal(self, pr):
        v_list = list(pr.variables())
        xx = v_list.pop(0)

        total = pr.element([1])
        for v in v_list:
            total *= xx - v

        generator_list = []
        for i in range(self.polynomial.degree()):
            xx_coeff = total.projection(0, i)
            generator_list.append(xx_coeff - self.polynomial[i])

        return pr.ideal(generator_list)

    def _term(self, x0, x1, x2, x3):
        return x0 * x1 + x2 * x3
