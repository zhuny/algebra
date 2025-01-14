import collections
import functools

from algebra.group.abstract.set_action import MonomialActionGroupRep
from algebra.ring.polynomial.base import PolynomialRing, PolynomialRingElement
from algebra.ring.polynomial.naming import (
    VariableNameIndexGenerator,
    VariableNameListGenerator
)
from algebra.ring.polynomial.variable import CombineVariableSystem


def show(f):
    @functools.wraps(f)
    def wrapped(self, *args, **kwargs):
        print(f.__name__, 'start')
        result = f(self, *args, **kwargs)
        print(f.__name__, result)
        return result
    return wrapped


class GaloisGroupConstructor:
    def __init__(self, polynomial):
        self.polynomial = polynomial

        self.ring = None
        self.ideal = None
        self.mono_group = None

    def run(self):
        if self.is_alternative_subset():
            if self.is_dihedral_subset():
                return 'K4'
            else:
                return 'A4'
        if not self.is_dihedral_subset():
            return 'S4'
        elif self.is_cyclic_subset():
            return 'C4'
        else:
            return 'D8'

    @show
    def is_alternative_subset(self):
        """
        Polynomial의 discriminant가 square면 A4의 subset이다.
        :return:
        """
        disc = self.polynomial.discriminant()
        return disc.is_square()

    @show
    def is_dihedral_subset(self):
        return self.is_galois_subset(self.dihedral_invariant())

    @show
    def is_cyclic_subset(self):
        return self.is_galois_subset(self.cyclic_invariant())

    def dihedral_invariant(self):
        self._build_polynomial_ring()

        x = self.ring.variable.x
        x1 = x[0] * x[1]
        x2 = x[2] * x[3]
        return x1 * x1 + x2 * x2

    def cyclic_invariant(self):
        self._build_polynomial_ring()

        x = self.ring.variable.x
        answer = 0
        for i in range(4):
            answer += x[i-1] * x[i] * x[i]
        return answer

    def resolvent_polynomial(self, invariant_polynomial):
        orbit = []
        all_mult = self.ring.element([1])

        for g in self.mono_group.element_list():
            gx = g.act_polynomial(invariant_polynomial)
            if gx not in orbit:
                orbit.append(gx)

                all_mult *= self.ring.variable.y - gx
                all_mult %= self.ideal

        return all_mult

    def is_galois_subset(self, invariant_polynomial):
        resolvent = self.resolvent_polynomial(invariant_polynomial)
        resolvent = resolvent.projection_ring(self.ring.variable.y)

        for f, e in resolvent.factorize():
            f: PolynomialRingElement
            if f.degree() == 1:
                self.ideal /= invariant_polynomial - f[0]
                print(invariant_polynomial - f[0])
                input()
                return True

        return False

    def _build_ideal(self, pr):
        degree_dict = {0: pr.element([1])}

        for v1 in pr.variable.x:
            new_degree = collections.defaultdict(int)
            for k, v2 in degree_dict.items():
                new_degree[k+1] += v2
                new_degree[k] -= v1 * v2
            degree_dict = new_degree

        degree_dict.pop(max(degree_dict))

        return pr.ideal([
            v - self.polynomial[k]
            for k, v in degree_dict.items()
        ])

    def _build_polynomial_ring(self):
        if self.ring is not None:
            return

        degree = self.polynomial.degree()

        v_system = CombineVariableSystem([
            VariableNameIndexGenerator('x', degree),
            VariableNameListGenerator('y')
        ])

        pr = PolynomialRing(
            self.polynomial.ring.field,
            variable_system=v_system
        )

        # assign
        self.ring = pr
        self.ideal = self._build_ideal(pr)
        self.mono_group = MonomialActionGroupRep(pr.variable.x).as_group()
