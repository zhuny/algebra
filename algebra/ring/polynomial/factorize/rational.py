from algebra.field.finite_prime import FinitePrimeField
from algebra.number.util import prime_iter
from algebra.ring.polynomial.base import PolynomialRing
from algebra.ring.polynomial.factorize.base import (
    AlgorithmPipeline, Pipeline, PolynomialData
)


class FactorizePolynomialRational(AlgorithmPipeline):
    def get_pipeline(self):
        yield ConvertToFiniteFactorization()


class ConvertToFiniteFactorization(Pipeline):
    def run_one(self, data: PolynomialData):
        if data.polynomial.is_one():
            return

        current = data.polynomial
        polynomial = self._make_it_finite(data)
        prime = polynomial.ring.field.get_char()

        for f, e in polynomial.factorize():
            f_new = f.convert(data.polynomial.ring)

            for k, v in f_new.value.items():
                if v * 2 > prime:
                    f_new.value[k] = v - prime

            if current % f_new == 0:
                yield PolynomialData(
                    polynomial=f_new.monic(),
                    power=e * data.power
                )
                current /= f_new

        if not current.monic().is_one():
            yield PolynomialData(
                polynomial=current,
                power=data.power
            )

    def _make_it_finite(self, data):
        int_polynomial = data.polynomial.to_integer()
        prime = self._get_valid_prime(int_polynomial)

        ring = PolynomialRing(FinitePrimeField(prime), number=1)

        return int_polynomial.convert(ring)

    def _get_valid_prime(self, polynomial, limit=None):
        disc = polynomial.discriminant(0)
        if disc == 0:
            raise ValueError("Square Free Polynomial should be given")

        max_value = max([
            abs(v.value)
            for v in polynomial.value.values()
        ])
        max_value = max(max_value * 2, 10)
        if limit is not None:
            max_value = min(max_value, limit)

        for prime in prime_iter():
            if prime > max_value and disc % prime != 0:
                return prime
