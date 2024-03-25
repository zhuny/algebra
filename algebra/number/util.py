import collections
import itertools
import math
from typing import Dict, List

from algebra.util.queue import HeapQueueSet


def is_prime(num: int) -> bool:
    # More efficient algorithm is needed
    for i in range(2, num):
        if i * i > num:
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
    while num >= p * p:
        if num % p == 0:
            num //= p
            factor[p] += 1
        else:
            p += 2

    if num != 1:
        factor[num] += 1

    return factor


def lcm(a, b):
    return a * b // math.gcd(a, b)


def divisor_function(number):
    n = 1
    for p, e in factorize(number).items():
        n *= e + 1
    return n


def divisor_list(number) -> List[int]:
    if number == 1:
        yield 1
        return

    factor = factorize(number)
    queue = HeapQueueSet()
    queue.push(1)
    last = []

    while queue.size() > 0:
        i = queue.pop()
        yield i
        if number > i * i:
            last.append(number // i)
            for p in factor:
                if number % (j := p * i) == 0 and j * j <= number:
                    queue.push(j)

    last.reverse()
    yield from last


def _is_divisible(p, p_list):
    for i in p_list:
        if i * i > p:
            break
        if p % i == 0:
            return True

    return False


def prime_list():
    yield 2

    p_list = [3, 5, 7, 11, 13]
    yield from p_list

    for p in itertools.count(17, 2):
        if not _is_divisible(p, p_list):
            p_list.append(p)
            yield p
