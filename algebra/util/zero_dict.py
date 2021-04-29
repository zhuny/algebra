import collections


class ZeroValueSkip(collections.defaultdict):
    def __init__(self, *args, **kwargs):
        super().__init__(int, *args, **kwargs)

    def __setitem__(self, key, value):
        if value == 0:
            self.pop(key, value)
        else:
            return super().__setitem__(key, value)
