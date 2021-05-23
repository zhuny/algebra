import collections
from fractions import Fraction


class ZeroValueSkip(collections.defaultdict):
    def __init__(self, *args, **kwargs):
        super().__init__(Fraction, *args, **kwargs)

    def __setitem__(self, key, value):
        if value == 0:
            self.pop(key, value)
        else:
            return super().__setitem__(key, value)
