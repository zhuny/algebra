import functools
import itertools
from fractions import Fraction

from algebra.polynomial.multi_variable import MultiVariableRing, \
    MultiVariableElement, Monomial
from algebra.polynomial.polynomial import Polynomial


class BuchbergerAlgorithm:
    def __init__(self, element_list: list[MultiVariableElement]):
        self.element_list = element_list
        self.result = []
        self.output = []
        self.degree = 0

    def calc_degree(self):
        mono_list = [mono for mono, _ in self.output]
        lcm = functools.reduce(
            self.common_multiplier,
            mono_list
        )
        permutation_set = [list(range(p)) for p in lcm.power]
        degree = 0
        for p in itertools.product(*permutation_set):
            new_mono = Monomial(power=list(p), ring=lcm.ring)
            for mono in mono_list:
                if new_mono.is_divisible(mono):
                    break
            else:
                degree += 1
        self.degree = degree

    def run(self):
        for element in self.element_list:
            element = self.get_reduce(element)
            self.append_result(element)

        for e1, e2 in self.element_pair_iter():
            s_poly = self.s_polynomial(e1, e2)
            s_poly = self.get_reduce(s_poly)
            self.append_result(s_poly)

        self.calc_degree()

    def append_result(self, element):
        if self.is_zero(element):
            return

        self.result.append(element)

        element_mono = element.lead_monomial()
        self.output = [
            (prev_mono, prev)
            for prev_mono, prev in self.output
            if not prev_mono.is_divisible(element_mono)
        ]
        self.output.append((element_mono, element))

        print(element_mono)
        self.show(element)

    def element_pair_iter(self):
        i = 0
        while i < len(self.result):
            for j in range(i):
                yield self.result[j], self.result[i]
            i += 1

    def s_polynomial(self, e1: MultiVariableElement, e2: MultiVariableElement):
        e1_mono = e1.lead_monomial()
        e1_c = e1.lead_coefficient()
        e2_mono = e2.lead_monomial()
        e2_c = e2.lead_coefficient()

        e3 = self.common_divisor(e1_mono, e2_mono)

        return (
                self.to_element(e2_mono / e3) * e1 / e1_c -
                self.to_element(e1_mono / e3) * e2 / e2_c
        )

    def to_element(self, monomial):
        return MultiVariableElement(
            ring=monomial.ring,
            coefficient={monomial: 1}
        )

    def common_divisor(self, e1_mono, e2_mono):
        return Monomial(
            power=[min(x, y) for x, y in zip(e1_mono.power, e2_mono.power)],
            ring=e1_mono.ring
        )

    def common_multiplier(self, e1_mono, e2_mono):
        return Monomial(
            power=[max(x, y) for x, y in zip(e1_mono.power, e2_mono.power)],
            ring=e1_mono.ring
        )

    def get_reduce(self, element: MultiVariableElement, monic=True) -> MultiVariableElement:
        for another in self.result:
            element %= another
        if monic:
            element /= element.lead_coefficient()
        return element

    def is_zero(self, element: MultiVariableElement) -> bool:
        return len(element.coefficient) == 0

    def show(self, element: MultiVariableElement):
        for coefficient, value in element.coefficient.items():
            print(coefficient, value)
        print()

    def minimal_polynomial(self, element: MultiVariableElement):
        reduce_algorithm = RowReducedAlgorithm()

        reduce_algorithm.add_row(Polynomial({0: 1}), element.ring.constant(1))

        current = element
        for i in range(1, self.degree + 1):
            current = self.get_reduce(current, monic=False)
            reduce_algorithm.add_row(Polynomial({i: 1}), current)
            current *= element

        reduce_algorithm.run()
        for row in reduce_algorithm.row_list:
            print(row.polynomial)
            self.show(row.element)


class RowReducedAlgorithm:
    def __init__(self):
        self.row_list = []

    def run(self):
        for row1, row2 in itertools.combinations(self.row_list, 2):
            row2.sub(row1)

    def add_row(self, poly: Polynomial, element: MultiVariableElement):
        self.row_list.append(Row(poly, element))


class Row:
    def __init__(self, polynomial: Polynomial, element: MultiVariableElement):
        self.polynomial = polynomial
        self.element = element

    def sub(self, row: 'Row'):
        lead_mono = row.element.lead_monomial()
        lead_coeff = row.element.lead_coefficient()
        if lead_coeff == 0:
            return

        sub_value = self.element[lead_mono] / lead_coeff

        self.polynomial -= row.polynomial * sub_value
        self.element -= sub_value * row.element


def pow_gen(x, n):
    current = x
    for i in range(1, n):
        current *= x
    return current


def example1():
    ring = MultiVariableRing(3)
    x, y, z = ring.variables()

    f1 = pow_gen(x - y, 3) - z * z
    f2 = pow_gen(z - x, 3) - y * y
    f3 = pow_gen(y - z, 3) - x * x

    dc = BuchbergerAlgorithm([f1, f2, f3])
    dc.run()

    for mono, poly in dc.output:
        print(mono)
    dc.show(dc.get_reduce(pow_gen(x, 10)))


def example2():
    ring = MultiVariableRing(2)
    x, y = ring.variables()

    f1 = x * x - y * y / 7 - 5
    f2 = y * y + 4 * x - Fraction(7, 2)

    dc = BuchbergerAlgorithm([f1, f2])
    dc.run()

    dc.minimal_polynomial(3 * x - 2 * y)


def main():
    example1()
    example2()


if __name__ == '__main__':
    main()
