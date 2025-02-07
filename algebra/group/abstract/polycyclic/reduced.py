class PolyCyclicRow:
    def __init__(self, element, rows=None):
        self.element = element
        self.rows = rows or []

    def __add__(self, other):
        return type(self)(
            self.element + other.element,
            [a + b for a, b in zip(self.rows, other.rows)]
        )

    def __sub__(self, other):
        return type(self)(
            self.element - other.element,
            [a - b for a, b in zip(self.rows, other.rows)]
        )

    def __mul__(self, other: int):
        assert other >= 1
        current = self
        for _ in range(1, other):
            current += self
        return current

    def normalize(self):
        min_index = self.min_index()
        lead_num = self.element.power[min_index]
        degree = self.element.group.degree
        assert lead_num > 0
        power = pow(lead_num, degree - 2, degree)
        return self * power

    def is_identity(self):
        return self.element.is_identity()

    def min_index(self):
        raise NotImplementedError(self)

    def sub(self, other):
        other_mi = other.min_index()
        number = self.element.power[other_mi]
        if number > 0:
            return self - other * number
        else:
            return self


class PolyCyclicRightRow(PolyCyclicRow):
    def min_index(self):
        return self.element.max_index()


class PolyCyclicLeftRow(PolyCyclicRow):
    def min_index(self):
        return self.element.min_index()


class PolyCyclicRowReduced:
    def __init__(self, align=False):
        self.index_map = {}
        self.align = align

    def get_row(self, e, rows):
        if self.align:
            return PolyCyclicRightRow(e, rows)
        else:
            return PolyCyclicLeftRow(e, rows)

    def append_mult(self, e, rows=None):
        g = self.get_row(e, rows)
        self._append_power(g)
        self._append_commute(g)

    def _append_power(self, g):
        d = g.element.group.degree
        while not g.is_identity():
            self._append_one(g)
            g *= d

    def _append_commute(self, g):
        if g.is_identity():
            return

        index_item = list(self.index_map.items())
        for _, e in index_item:
            self._append_one(g + e - g - e)

    def reduce(self, e, rows=None):
        return self._append_one(self.get_row(e, rows), insert=False)

    def _append_one(self, g: 'PolyCyclicRow', insert=True):
        while not g.is_identity():
            g = g.normalize()
            gmi = g.min_index()
            if gmi in self.index_map:
                g -= self.index_map[gmi]
            else:
                if insert:
                    self.index_map[gmi] = g
                break

        return g

    def arrange_reverse(self):
        result = []
        for i, g in self.get_sorted_map():
            result = [(i1, g1.sub(g)) for i1, g1 in result]
            result.append((i, g))

        self.index_map = dict(result)

    def get_reduced(self):
        return [
            row.element
            for _, row in self.get_sorted_map()
        ]

    def get_sorted_map(self):
        return sorted(self.index_map.items(), reverse=self.align)

    def pop_index(self, row):
        power = list(row.element.power)
        for i, e in self.get_sorted_map():
            power.pop(i)  # every value must be 0
        return power
