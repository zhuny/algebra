import itertools
from dataclasses import dataclass

from algebra.ring.polynomial.base import PolynomialRingElement


class FactorizePolynomialFinite:
    def __init__(self, polynomial):
        self.polynomial = polynomial

    @staticmethod
    def get_pipeline():
        yield SquareFreeFactorization()
        yield DistinctDegreeFactorization()

    def run(self):
        stream = [PolynomialData(polynomial=self.polynomial)]

        for pipe in self.get_pipeline():
            stream = pipe.run(stream)

        for s in stream:
            print(s.polynomial, s.power, s.degree)
            input()


@dataclass
class PolynomialData:
    polynomial: PolynomialRingElement
    power: int = 1

    # context
    degree: int = 0


class Pipeline:
    def run(self, stream):
        for d in stream:
            yield from self.run_one(d)

    def run_one(self, data: PolynomialData):
        raise NotImplementedError(self)


class SquareFreeFactorization(Pipeline):
    def run_one(self, data: PolynomialData):
        poly = data.polynomial

        c = poly.gcd(poly.diff(0).monic())
        w = poly / c
        i = 1

        while w != 1:
            y = w.gcd(c)
            yield PolynomialData(polynomial=(w / y).monic(), power=i)
            w, c = y, c / y
            i += 1

        if c != 1:
            print('SFF :', c)
            assert False


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
