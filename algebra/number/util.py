import collections
from typing import List, Dict


def is_prime(num: int) -> bool:
    # More efficient algorithm is needed
    for i in range(2, num):
        if i*i > num:
            return True
        if num % i == 0:
            return False
    return True


def factorize(num: int) -> Dict[int, int]:
    if num <= 0:
        raise ValueError("Integer is needed")

    # More efficient algorithm is needed

    factor = collections.defaultdict(int)
    while num % 2 == 0:
        factor[2] += 1
        num >>= 1

    p = 3
    while num >= p*p:
        if num % p == 0:
            num //= p
            factor[p] += 1
        else:
            p += 2

    if num != 1:
        factor[num] += 1

    return factor
