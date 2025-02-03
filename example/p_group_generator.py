from algebra.group.abstract.polycyclic.base import PolyCyclicGroupRep


def main():
    # C2 X C2
    g = PolyCyclicGroupRep(2, 2).as_group()

    pcg = g.p_covering_group()
    pcg.show('Normalized')
    print(pcg.order())

    for group in pcg.lower_exponent_p_central_series():
        print(group)

    ag = pcg.automorphism_group()
    print(ag)

    pm = pcg.p_multiplicator()
    print(pm)


if __name__ == '__main__':
    main()
