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
            lambda x, y: x.lcm(y),
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

    def show(self):
        print("Result:")
        for i, element in enumerate(self.result):
            print(f'{i}.', element)
        print("Output:")
        for mono, element in self.output:
            print(mono, element)
        input()

    def run(self):
        for element in self.element_list:
            self.append_result(element)
            # self.show()

        for e1, e2 in self.element_pair_iter():
            self.append_result(e1.s_polynomial(e2))
            # self.show()

        self.calc_degree()

    def append_result(self, element):
        element = self.get_reduce(element)

        if element.is_zero():
            return

        self.result.append(element)

        # reduced form
        element_monomial = element.lead_monomial()
        for monomial, prev in self.output:
            if element_monomial.is_divisible(monomial):
                return

        new_output = []

        for monomial, prev in self.output:
            if monomial.is_divisible(element_monomial):
                continue

            new_output.append((monomial, prev % element))

        new_output.append((element_monomial, element))
        self.output = new_output

    def element_pair_iter(self):
        i = 0
        while i < len(self.result):
            for j in range(i):
                yield self.result[j], self.result[i]
            i += 1

    def get_reduce(self, element: PolynomialRingElement, monic=True
                   ) -> PolynomialRingElement:
        skip = 0
        for another in self.repeat_output():
            q, element = divmod(element, another)
            if q.is_zero():
                skip += 1
                if skip >= len(self.output):
                    break
            else:
                skip = 0

        if monic and not element.lead_coefficient().is_zero():
            element /= element.lead_coefficient()

        return element

    def repeat_output(self):
        while self.output:
            for _, element in self.output:
                yield element

    def get_basis(self):
        return [element for _, element in self.output]

    def minimal_polynomial(self, element: PolynomialRingElement):
        result_ring = PolynomialRing(field=element.ring.field, number=1)

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
