import math

from algebra.field.radical.base import ODRadical


def main():
    sqrt2 = ODRadical.from_number(2)
    sqrt3 = ODRadical.from_number(3)

    number = sqrt2 + sqrt3
    print(number)
    print(math.floor(number))


if __name__ == '__main__':
    main()
