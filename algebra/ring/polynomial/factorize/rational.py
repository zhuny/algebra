from algebra.field.finite_prime import FinitePrimeField
from algebra.number.util import prime_iter
from algebra.ring.polynomial.base import PolynomialRingElement, PolynomialRing


class FactorizePolynomialRational:
    def __init__(self, polynomial):
        self.polynomial: PolynomialRingElement = polynomial

    def run(self):
        prime = self._get_valid_prime()

        ring = PolynomialRing(FinitePrimeField(prime))

        polynomial = self.polynomial.convert(ring)
        for f, e in polynomial.factorize():
            f_new = f.convert(self.polynomial.ring)

            if self.polynomial % f_new == 0:
                yield f_new, e
            else:
                raise ValueError("????")

    def _get_valid_prime(self):
        disc = self.polynomial.discriminant(0)
        max_value = max([
            abs(v.value)
            for v in self.polynomial.value.values()
        ])
        max_value = max(max_value * 2, 10)

        for prime in prime_iter():
            if prime > max_value and disc % prime != 0:
                return prime
