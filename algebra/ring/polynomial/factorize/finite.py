from dataclasses import dataclass

from algebra.ring.polynomial.base import PolynomialRingElement


class FactorizePolynomialFinite:
    def __init__(self, polynomial):
        self.polynomial = polynomial

    @staticmethod
    def get_pipeline():
        yield SquareFreeFactorization()

    def run(self):
        stream = [PolynomialData(polynomial=self.polynomial)]

        for pipe in self.get_pipeline():
            stream = pipe.run(stream)

        for s in stream:
            print(s.polynomial)
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
            yield PolynomialData(polynomial=w / y, power=i)
            w, c = y, c / y
            i += 1
