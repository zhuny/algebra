import itertools
from operator import itemgetter

from algebra.number.util import divisor_function, divisor_list
from algebra.ring.polynomial.base import PolynomialRingElement


def divisor_list_wrap(n):
    if n == 0:
        return [0]
    else:
        factor_list = list(divisor_list(abs(n)))
        factor_list.extend([-d for d in factor_list])
        return factor_list


class FactorizePolynomialRational:
    def __init__(self, polynomial: PolynomialRingElement):
        self.polynomial = polynomial

    def run(self):
        if self.polynomial.ring.number != 1:
            return []

        degree = sum(self.polynomial.lead_monomial().power)
        if degree < 2:
            return [self]

        many = degree // 2

        value = [
            (
                i,
                (v := int(self.polynomial([i]))),
                divisor_function(abs(v)) * 2 if v != 0 else 1
            )
            for i in range(-100, 100)
        ]
        value.sort(key=itemgetter(2, 1, 0))
        picked = value[:many]
        picked_factor = [divisor_list_wrap(v[1]) for v in picked]
        checker = value[many]

        for each_value in itertools.product(*picked_factor):
            solved: PolynomialRingElement = self.solve_value({
                x[0]: z
                for x, z in zip(picked, each_value)
            })
            if solved.is_constant():
                continue
            if not self.is_valid_value(checker[1], solved(checker[0])):
                continue

            q, r = divmod(self.polynomial, solved)
            if r == 0:
                return solved.factorize() + q.factorize()

        return [self]
