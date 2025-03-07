import itertools
import random

from algebra.exception.me import IncorrectError
from algebra.ring.polynomial.factorize.base import AlgorithmPipeline, \
    PolynomialData, Pipeline

"""
Implementation Reference
https://en.wikipedia.org/wiki/Factorization_of_polynomials_over_finite_fields
"""


class FactorizePolynomialFinite(AlgorithmPipeline):
    def get_pipeline(self):
        yield SquareFreeFactorization()
        yield DistinctDegreeFactorization()
        yield CantorZassenhausAlgorithm()

    def run(self):
        result = list(super().run())
        current = 1

        for polynomial, power in result:
            for i in range(power):
                current *= polynomial

        if self.polynomial != current:
            print("Factor :")
            for polynomial, power in result:
                print(polynomial, power)
            print("Expected :", self.polynomial)
            print("Calc :", current)
            raise IncorrectError(self.polynomial, current)

        yield from result


class SquareFreeFactorization(Pipeline):
    def run_one(self, data: PolynomialData):
        poly = data.polynomial

        d = poly.diff(0)
        if d.is_zero():
            yield self.run_with_p(data)
            return

        c = poly.gcd(d.monic())
        w = poly / c
        i = 1

        while w != 1:
            y = w.gcd(c)
            yield PolynomialData(
                polynomial=(w / y).monic(),
                power=i*data.power
            )
            w, c = y, c / y
            i += 1

        if c != 1:
            yield self.run_with_p(
                PolynomialData(polynomial=c, power=data.power)
            )

    def run_with_p(self, data: PolynomialData):
        degree = data.polynomial.ring.field.char
        polynomial = data.polynomial.ring.element({
            k.root(degree): v
            for k, v in data.polynomial.value.items()
        })
        return self.run_one(
            PolynomialData(
                polynomial=polynomial,
                power=data.power * degree
            )
        )


class DistinctDegreeFactorization(Pipeline):
    def run_one(self, data: PolynomialData):
        poly = data.polynomial.monic()
        if poly == 1:
            return

        q = poly.ring.field.size()

        for i in itertools.count(1):
            if poly.degree() < 2 * i:
                break

            total_mult = poly.ring.element({
                1: -1,
                (q ** i): 1
            })
            g = poly.gcd(total_mult)
            if g != 1:
                yield PolynomialData(
                    polynomial=g,
                    power=data.power, degree=i
                )
                poly /= g

        if poly != 1:
            yield PolynomialData(
                polynomial=poly,
                power=data.power, degree=poly.degree()
            )


class CantorZassenhausAlgorithm(Pipeline):
    def run_one(self, data: PolynomialData):
        factors = [data.polynomial]
        factor_size = data.polynomial.degree() // data.degree
        field_size = data.polynomial.ring.field.size()

        while len(factors) < factor_size:
            h = self.get_random_poly(
                data.polynomial.ring,
                data.polynomial.degree()
            )
            h = pow(h, (field_size ** data.degree - 1) // 2, data.polynomial)
            h = (h - 1) % data.polynomial

            factors = list(self.split_factor(factors, h))

        for factor in factors:
            yield PolynomialData(polynomial=factor, power=data.power)

    @staticmethod
    def get_random_poly(ring, max_degree):
        random_degree = random.randint(3, max_degree + 1)
        size = ring.field.size()
        return ring.element([
            random.randint(0, size-1)
            for i in range(random_degree)
        ])

    @staticmethod
    def split_factor(factors, choice):
        for factor in factors:
            left = factor.gcd(choice)
            if left != 1 and left != factor:
                yield left
                yield factor / left
            else:
                yield factor
