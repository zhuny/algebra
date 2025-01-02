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

    def get_pipeline(self):
        raise NotImplementedError(self)

    def run(self):
        stream = [PolynomialData(polynomial=self.polynomial)]

        for pipe in self.get_pipeline():
            stream = pipe.run(stream)

        return stream
