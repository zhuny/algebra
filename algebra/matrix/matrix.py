import collections
from fractions import Fraction


class Matrix:
    def __init__(self, row: int = 0, col: int = 0):
        self.body = {}
        self.row_size = row
        self.col_size = col

    def __str__(self):
        col_str_max = collections.defaultdict(list)
        matrix_str = {}

        for row in range(self.row_size):
            for col in range(self.col_size):
                s = str(self[row, col])
                col_str_max[col].append(s)
                matrix_str[row, col] = s

        stream = []
        col_padding = {
            k: max(map(len, v))
            for k, v in col_str_max.items()
        }
        for row in range(self.row_size):
            for col in range(self.col_size):
                s = matrix_str[row, col]
                stream.append(s)
                stream.append(' ' * (col_padding[col] + 1 - len(s)))
            stream.append('\n')

        return ''.join(stream)

    def copy(self):
        m = Matrix(self.row_size, self.col_size)
        for k, v in self.body.items():
            m[k] = v
        return m

    def append_row(self):
        self.row_size += 1

    def append_col(self):
        self.col_size += 1

    # getitem, setitem for memory optimization
    def __getitem__(self, item):
        row, col = item
        if 0 <= row < self.row_size and 0 <= col < self.col_size:
            return self.body.get(item, Fraction())
        else:
            raise ValueError("Index out of matrix size")

    def __setitem__(self, key, value):
        row, col = key
        if 0 <= row < self.row_size and 0 <= col < self.col_size:
            if value:
                self.body[row, col] = value
            else:
                self.body.pop((row, col), None)
        else:
            raise ValueError("Index out of matrix size")

    def _div_row(self, row, value):
        if value == 1:
            return
        for col in range(self.col_size):
            self[row, col] /= value

    def _add_row(self, row_s, row_t, value):
        for col in range(self.col_size):
            self[row_t, col] += self[row_s, col] * value

    def _find_non_zero(self, row, col):
        for row2 in range(row, self.row_size):
            if self[row2, col]:
                return row2

    def _swap_row(self, row1, row2):
        for col in range(self.col_size):
            self[row1, col], self[row2, col] = self[row2, col], self[row1, col]

    def reduced_form(self, associate=None):
        col = 0
        for row in range(self.row_size):
            while col < self.col_size:
                row2 = self._find_non_zero(row, col)
                if row2 is None:
                    col += 1
                    continue
                else:
                    if row != row2:
                        self._swap_row(row, row2)
                        associate[row], associate[row2] = (
                            associate[row2], associate[row]
                        )
                    break

            if col == self.col_size:
                break

            associate[row] /= self[row, col]
            self._div_row(row, self[row, col])

            for row2 in range(self.row_size):
                if row == row2:
                    continue
                associate[row2] -= associate[row] * self[row2, col]
                self._add_row(row, row2, -self[row2, col])

    def is_zero_row(self, row):
        for col in range(self.col_size):
            if self[row, col]:
                return False
        return True

    def to_wolfram_alpha(self):
        stream = ["{"]
        for row in range(self.row_size):
            if row > 0:
                stream.append(",")
            stream.append("{")
            for col in range(self.col_size):
                if col > 0:
                    stream.append(",")
                stream.append(str(self[row, col]))
            stream.append("}")
        stream.append("}")
        return "".join(stream)

    def determinant(self):
        clone = self.copy()
        answer = 1
        for i in range(self.col_size):
            if clone[i, i] == 0:
                for j in range(i, self.col_size):
                    if clone[i, j] != 0:
                        clone._swap_row(i, j)
                        break

            value = clone[i, i]
            if value == 0:
                return value  # return zero

            answer *= value

            clone._div_row(i, value)
            for j in range(i+1, self.col_size):
                clone._add_row(i, j, -clone[j, i])

        return answer
