import functools

from algebra.field.rational import RationalField
from algebra.ring.polynomial.base import PolynomialRing
from algebra.ring.polynomial.monomial_ordering import \
    LexicographicMonomialOrdering, MonomialOrderingBase, \
    GradedLexicographicOrdering, GradedReverseLexicographicOrdering


class AssertWrap:
    def __init__(self, f, args, kwargs):
        self.f = f
        self.args = args
        self.kwargs = kwargs

    def run(self):
        return self.f(*self.args, **self.kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, AssertionError):
            print(self.f.__name__, self.args, self.kwargs, 'Error')
        else:
            print(self.f.__name__, 'OK')


def assert_wrap(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with AssertWrap(f, args, kwargs) as wrap:
            return wrap.run()
    return wrapper


@assert_wrap
def test_one_monomial_ordering(ordering: MonomialOrderingBase,
                               number: int, constant: bool,
                               answer: list[str]):
    pr = PolynomialRing(
        field=RationalField(), number=number,
        monomial_ordering=ordering
    )
    f = pr.one() if constant else pr.zero()
    f = sum(pr.variables(), start=f)
    f = f * f

    ordered_monomial = list(f.sorted_monomial())

    assert len(ordered_monomial) == len(answer)

    for result, expected in zip(ordered_monomial, answer):
        assert str(result) == expected


def test_monomial_ordering():
    test_one_monomial_ordering(
        LexicographicMonomialOrdering(),
        2, True,
        ["x^2", "xy", "x", "y^2", "y", ""]
    )
    test_one_monomial_ordering(
        GradedLexicographicOrdering(),
        2, True,
        ["x^2", "xy", "y^2", "x", "y", ""]
    )
    test_one_monomial_ordering(
        GradedLexicographicOrdering(),
        3, False,
        ["x^2", "xy", "xz", "y^2", "yz", "z^2"]
    )
    test_one_monomial_ordering(
        GradedReverseLexicographicOrdering(),
        3, False,
        ["x^2", "xy", "y^2", "xz", "yz", "z^2"]
    )


def main():
    test_monomial_ordering()


if __name__ == "__main__":
    main()
