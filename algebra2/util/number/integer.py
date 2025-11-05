from algebra2.group.base import AppBaseModel


class Factor(AppBaseModel):
    base: int
    power: int


class FactorizationResult(AppBaseModel):
    number: int
    factor: list[Factor]


def factorize(number: int) -> FactorizationResult:
    given_number = number
    factor = []

    for i in range(2, number):
        if number < i * i:
            break

        power = 0
        while number % i == 0:
            power += 1
            number //= i
        if power > 0:
            factor.append(Factor(base=i, power=power))

    if number > 1:
        factor.append(Factor(base=number, power=1))

    return FactorizationResult(number=given_number, factor=factor)
