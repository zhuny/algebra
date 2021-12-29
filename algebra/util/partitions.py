import itertools


def integer_partition_with_max(n: int, i: int):
    assert n >= 1 and i >= 1

    if n < i:
        return 0
    if n == i:
        return 1
    if i == 1:
        return 1

    total = 0
    for j in range(1, i + 1):
        total += integer_partition_with_max(n - i, j)
    return total


def integer_partition(n):
    total = 0
    for i in range(1, n + 1):
        total += integer_partition_with_max(n, i)
    return total


def prev_partition():
    step = 0
    sign = 1
    for i in itertools.count(1):
        step += 2 * i - 1
        yield step, sign
        step += i
        yield step, sign
        sign = -sign


def integer_partition2(n):
    result = [1]
    for i in range(1, n + 1):
        total = 0
        for j, sign in prev_partition():
            if i >= j:
                total += result[i - j] * sign
            else:
                break
        result.append(total)
    return result[-1]


def run():
    answer_list = [1, 2, 3, 5, 7, 11, 15]
    for i, answer in enumerate(answer_list, 1):
        calculated = integer_partition(i)
        if calculated == answer:
            print(f"partition({i}) = {calculated}")
        else:
            print(f"{calculated=}, {answer=}")

    for i in range(1, 41):
        calculated = integer_partition(i)
        calculated_fast = integer_partition2(i)
        print(f"partition({i}) = {calculated} =? {calculated_fast}")


if __name__ == '__main__':
    run()
