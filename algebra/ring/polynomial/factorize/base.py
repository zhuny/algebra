from dataclasses import dataclass

from algebra.ring.polynomial.base import PolynomialRingElement


@dataclass
class PolynomialData:
    polynomial: PolynomialRingElement
    power: int = 1

    # context
    degree: int = 0


class AlgorithmPipeline:
    def __init__(self, polynomial):
        self.polynomial = polynomial.monic()

    def get_pipeline(self) -> list['Pipeline']:
        raise NotImplementedError(self)

    def run(self):
        stream = [PolynomialData(polynomial=self.polynomial)]

        for pipe in self.get_pipeline():
            stream = pipe.run(stream)

        for s in stream:
            yield s.polynomial, s.power


class Pipeline:
    def run(self, stream):
        for d in stream:
            stack = [self.run_one(d)]
            while stack:
                top = stack.pop()
                for element in top:
                    if isinstance(element, PolynomialData):
                        yield element
                    else:
                        stack.append(top)
                        stack.append(element)
                        break

    def run_one(self, data: PolynomialData):
        raise NotImplementedError(self)
