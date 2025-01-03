import math
from fractions import Fraction

from algebra.field.finite_prime import FinitePrimeField
from algebra.number.util import prime_iter
from algebra.ring.polynomial.base import PolynomialRing
from algebra.ring.polynomial.factorize.base import AlgorithmPipeline, Pipeline, \
    PolynomialData
from algebra.ring.polynomial.factorize.finite import SquareFreeFactorization


class FactorizePolynomialRational(AlgorithmPipeline):
    def get_pipeline(self):
        yield SquareFreeFactorization()
        yield ConvertToFiniteFactorization()


class ConvertToFiniteFactorization(Pipeline):
    def run_one(self, data: PolynomialData):
        if data.polynomial.is_one():
            return

        int_polynomial = self._to_integer(data.polynomial)
        prime = self._get_valid_prime(int_polynomial)

        ring = PolynomialRing(FinitePrimeField(prime))

        polynomial = int_polynomial.convert(ring)
        for f, e in polynomial.factorize():
            f_new = f.convert(data.polynomial.ring)

            if int_polynomial % f_new == 0:
                yield PolynomialData(
                    polynomial=f_new.monic(),
                    power=e * data.power
                )
            else:
                raise ValueError(f'{int_polynomial} % {f_new}')

    def _to_integer(self, polynomial):
        # rational to integer
        answer = 1
        for c in polynomial.value.values():
            v: Fraction = c.value
            answer = math.lcm(answer, v.denominator)
        return polynomial * answer

    def _get_valid_prime(self, polynomial):
        disc = polynomial.discriminant(0)
        if disc == 0:
            raise ValueError("Square Free Polynomial should be given")
        max_value = max([
            abs(v.value)
            for v in polynomial.value.values()
        ])
        max_value = max(max_value * 2, 10)

        for prime in prime_iter():
            if prime > max_value and disc % prime != 0:
                return prime
