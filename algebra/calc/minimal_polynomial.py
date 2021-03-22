import itertools
from fractions import Fraction

from algebra.matrix.matrix import Matrix
from algebra.number.radical import Radical
from algebra.polynomial.polynomial import Polynomial


class Counter:
    def __init__(self):
        self.body = {}

    def get(self, obje):
        return self.body.setdefault(obje, len(self.body))


class ComponentMap:
    def __init__(self, counter):
        self.body = {}
        self.counter = counter

    def set(self, key, value):
        self.body[self.counter.get(key)] = value


class MappedColumnMatrix:
    def __init__(self):
        self.matrix = Matrix()
        self.counter = Counter()

    def append_row(self):
        self.matrix.append_row()

    def set_last(self, index, number):
        row = self.matrix.row_size-1
        col = self.counter.get(index)
        if col >= self.matrix.col_size:
            self.matrix.append_col()
        self.matrix[row, col] = number

    def reduced_form(self, right):
        self.matrix.reduced_form(right)

    def is_last_zero(self):
        return self.matrix.is_zero_row(self.matrix.row_size-1)


def minimal_polynomial(number: Radical):
    x = number

    left_matrix = MappedColumnMatrix()
    right_row = [Polynomial([1])]

    left_matrix.append_row()
    left_matrix.set_last((), Fraction(1))

    for i in itertools.count(1):
        left_matrix.append_row()
        if x.body.constant:
            left_matrix.set_last((), Fraction(x.body.constant, x.inv))
        for body in x.body.body:
            left_matrix.set_last(
                (body.index, body.radicand),
                Fraction(body.multiplier, x.inv)
            )

        right_row.append(Polynomial({i: 1}))
        left_matrix.reduced_form(right_row)

        # print(i)
        # for p, poly in enumerate(right_row):
        #     print(f"Polynomial[{p}] :", poly.to_wolfram_alpha())
        #
        # print(x.to_wolfram_alpha())
        # print(left_matrix.matrix.to_wolfram_alpha())
        # input()

        if left_matrix.is_last_zero():
            break

        x *= number

    return right_row[-1]
