import math

from algebra.field.radical.base import ODRadical


def calculate_number(number):
    print(number)
    print(math.floor(number))

    count = []
    for i in range(10):
        int_part = math.floor(number)
        count.append(int_part)
        number = (number - int_part).inv()

    print(count)
    print()


def main():
    sqrt2 = ODRadical.sqrt(2)
    sqrt3 = ODRadical.sqrt(3)

    # 음수 확인
    for i in range(-4, 5):
        for j in range(-4, 5):
            if i == j == 0:
                continue
            calculate_number(sqrt2 * i + sqrt3 * j)

    sqrt5 = ODRadical.sqrt(5)
    calculate_number(sqrt2 + sqrt3 + sqrt5)


if __name__ == '__main__':
    main()
