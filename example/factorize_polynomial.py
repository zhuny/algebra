import random
import time

from algebra.field.finite_prime import FinitePrimeField
from algebra.ring.polynomial.base import PolynomialRing, PolynomialRingElement


class ErrorDebug:
    def __init__(self, polynomial):
        self.polynomial = polynomial
        self.start = None

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            print("Check this polynomial")
            result = [0] * (self.polynomial.degree() + 1)
            for mono, mult in self.polynomial.value.items():
                result[mono.degree()] = mult.value
            print(result)
        else:
            print("DONE :", time.time() - self.start)


def build(pr) -> PolynomialRingElement:
    element = 1
    for _ in range(5):
        new_factor = pr.element([
            random.randint(0, 16)
            for _ in range(4)
        ])
        for _ in range(int(1.3 / (random.random()+0.2))):
            element *= new_factor
    return element.monic()


def main():
    pr = PolynomialRing(field=FinitePrimeField(17), number=1)

    for i in range(1000):
        e = build(pr)
        with ErrorDebug(e):
            print(e, '=')
            for f, p in e.factorize():
                print(f, p)
        print()


if __name__ == '__main__':
    main()
