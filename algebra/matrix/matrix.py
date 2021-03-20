from fractions import Fraction


class Matrix:
    def __init__(self):
        self.body = {}
        self.row_size = 0
        self.col_size = 0

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

    def _div(self, row, value):
        if value == 1:
            return
        for col in range(self.col_size):
            self[row, col] /= value

    def _add(self, row_s, row_t, value):
        for col in range(self.col_size):
            self[row_t, col] += self[row_s, col] * value

    def reduced_form(self, associate=None):
        col = 0
        for row in range(self.row_size):
            while col < self.col_size and self[row, col] == 0:
                col += 1
            if col == self.col_size:
                break

            associate[row] /= self[row, col]
            self._div(row, self[row, col])

            for row2 in range(self.row_size):
                if row == row2:
                    continue
                associate[row2] -= associate[row]*self[row2, col]
                self._add(row, row2, -self[row2, col])

    def is_zero_row(self, row):
        for col in range(self.col_size):
            if self[row, col]:
                return False
        return True
