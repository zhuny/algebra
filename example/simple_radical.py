import math

from algebra.field.radical.base import ODRadical


def calculate_number(number):
    print(number)
    print(math.floor(number))

    count = []
    for i in range(6):
        int_part = math.floor(number)
        count.append(int_part)
        number = (number - int_part).inv()
        print(number)
    print(count)
    print()


def main():
    sqrt2 = ODRadical.sqrt(2)
    sqrt3 = ODRadical.sqrt(3)

    for i in range(1, 6):
        for j in range(1, 6):
            calculate_number(sqrt2 * i + sqrt3 * j)


if __name__ == '__main__':
    main()
