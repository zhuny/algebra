import functools
import time


def iter_to_str(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs) -> str:
        return str(''.join(f(*args, **kwargs)))
    return wrapper


class Timer:
    def __init__(self, name):
        self.start = 0
        self.name = name

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(self.name, time.time() - self.start)
