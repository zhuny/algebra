import itertools

from algebra2.group.permutation.simple import cyclic_product
from algebra2.util.number.integer import factorize


def _generate_p_power_abelian(left: int, limit: int, prev: list[int]):
    if left == 0:
        yield list(prev)

    elif limit == 1:
        yield prev + [1] * left

    else:
        while left >= 0:
            yield from _generate_p_power_abelian(left, limit - 1, prev)
            left -= limit
            prev.append(limit)
        while prev and prev[-1] == limit:
            prev.pop()


def generate_p_power_abelian(base, total_power):
    for power_split in _generate_p_power_abelian(total_power, total_power, []):
        order_list = [base ** power for power in power_split]
        yield cyclic_product(order_list)


def generate_p_power(base, power):
    yield from generate_p_power_abelian(base, power)


def generate_from_order(order: int):
    factor = factorize(order)

    combined_cases = {}
    for f in factor.factor:
        combined_cases[f.base] = list(generate_p_power(f.base, f.power))

    if len(combined_cases) == 1:
        for k, v in combined_cases.items():
            yield from v

    elif len(combined_cases) == 2:
        for g1, g2 in itertools.product(*combined_cases.values()):
            yield g1.direct_product(g2)


def main():
    for i in range(1, 9):
        for group in generate_from_order(i):
            show_group('Given', group)
            show_group('Automorphism Group', group.automorphism_group())
            print()


def show_group(msg, g):
    print(msg, ':', g, g.order())


if __name__ == '__main__':
    main()
