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
    divisor_list = [1]

    for f in factor.factor:
        p_power = [1, f.base]
        for _ in range(1, f.power):
            p_power.append(p_power[-1] * f.base)
        divisor_list = [
            pp * d
            for pp in p_power
            for d in divisor_list
        ]

    combined_cases = {}
    for f in factor.factor:
        other = factor.number // (f.base ** f.power)
        conjugate_valid = [
            d for d in divisor_list
            if d % f.base == 1 and other % d == 0
        ]
        p_power_groups = list(generate_p_power(f.base, f.power))
        combined_cases[f.base] = [
            (g, d)
            for d in conjugate_valid
            for g in p_power_groups
        ]
        print(f.base, 'base')
        for g, d in combined_cases[f.base]:
            print('-', g, d)
    print(order)

    return []


def main():
    for i in range(6, 7):
        for group in generate_from_order(i):
            print(group)


if __name__ == '__main__':
    main()
