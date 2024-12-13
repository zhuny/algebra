import functools
import itertools

from algebra.ring.polynomial.base import PolynomialRingElement, Monomial, \
    PolynomialRing


class BuchbergerAlgorithm:
    def __init__(self, element_list: list[PolynomialRingElement]):
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
        if element.is_zero():
            return

        self.result.append(element)

        element_mono = element.lead_monomial()
        self.output = [
            (prev_mono, prev)
            for prev_mono, prev in self.output
            if not prev_mono.is_divisible(element_mono)
        ]
        self.output.append((element_mono, element))

    def element_pair_iter(self):
        i = 0
        while i < len(self.result):
            for j in range(i):
                yield self.result[j], self.result[i]
            i += 1

    def s_polynomial(self,
                     e1: PolynomialRingElement,
                     e2: PolynomialRingElement) -> PolynomialRingElement:
        if e1.is_zero() or e2.is_zero():
            return e1.ring.element([])

        e1_mono = e1.lead_monomial()
        e1_c = e1.lead_coefficient()
        e2_mono = e2.lead_monomial()
        e2_c = e2.lead_coefficient()

        e3 = e1_mono.gcd(e2_mono)

        return (
                (e2_mono / e3) * e1 / e1_c -
                (e1_mono / e3) * e2 / e2_c
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

    def get_reduce(self, element: PolynomialRingElement, monic=True
                   ) -> PolynomialRingElement:
        for another in self.result:
            element %= another
        if monic and element.lead_coefficient() != 0:
            element /= element.lead_coefficient()
        return element

    def is_zero(self, element: PolynomialRingElement) -> bool:
        return len(element.coefficient) == 0

    def minimal_polynomial(self, element: PolynomialRingElement):
        result_ring = PolynomialRing(element.ring.field)

        reduce_algorithm = RowReducedAlgorithm()
        reduce_algorithm.add_row(
            result_ring.element([1]),
            element.ring.element(1)
        )

        current = element
        for i in range(1, self.degree + 1):
            current = self.get_reduce(current, monic=False)
            reduce_algorithm.add_row(result_ring.element({i: 1}), current)
            current *= element

        return reduce_algorithm.run()


class RowReducedAlgorithm:
    def __init__(self):
        self.row_list: list[Row] = []

    def run(self):
        for row1, row2 in itertools.combinations(self.row_list, 2):
            row2.sub(row1)
        return self.row_list[-1].polynomial

    def add_row(self,
                poly: PolynomialRingElement, element: PolynomialRingElement):
        self.row_list.append(Row(poly, element))


class Row:
    def __init__(self,
                 polynomial: PolynomialRingElement,
                 element: PolynomialRingElement):
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
