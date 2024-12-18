import functools


def iter_to_str(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs) -> str:
        return str(''.join(f(*args, **kwargs)))
    return wrapper
