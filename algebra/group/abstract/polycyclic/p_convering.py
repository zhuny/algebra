from algebra.group.abstract.polycyclic.base import PolyCyclicGroupRep, \
    PolyCyclicGroup


class PCoveringGroupAlgorithm:
    def __init__(self, pc_group):
        self.group: PolyCyclicGroup = pc_group

    def run(self):
        rep: PolyCyclicGroupRep = self.group.represent
        result = PolyCyclicGroupRep(degree=rep.degree, number=rep.number)

        for i in range(rep.number):
            new_i = result.add_number()
            power_rel = (
                rep.power_relation.get(i, []) +
                [new_i]
            )
            result.power_relation[i] = power_rel

        for i in range(rep.number):
            for j in range(i):
                p = i, j
                new_p = result.add_number()
                result.commute_relation[p] = (
                    rep.commute_relation.get(p, []) + [new_p]
                )

        self.optimize(result)
        return result.as_group()

    def optimize(self, rep: PolyCyclicGroupRep):
        while self.optimize_once(rep):
            pass

    def optimize_once(self, rep: PolyCyclicGroupRep):
        # optimize
        for left, right in self.optimize_check_pair(rep):
            if left != right:
                diff = left - right
                if diff.is_identity():
                    diff = - left + right

                diff_index = diff.max_index()
                left = diff - rep.from_index(diff_index)
                rep.remove_index(diff_index, left.to_index_list())
                return True

        return False

    def optimize_check_pair(self, rep: PolyCyclicGroupRep):
        for ei in rep.generator_list():
            ei_p = ei * (rep.degree - 1)

            yield (ei + ei_p) + ei, ei + (ei_p + ei)

        for ei, ej in rep.generator_list(2):
            ei_p = ei * (rep.degree - 1)
            ej_p = ej * (rep.degree - 1)

            yield (ej_p + ej) + ei, ej_p + (ej + ei)
            yield (ej + ei) + ei_p, ej + (ei + ei_p)

        for ei, ej, ek in rep.generator_list(3):
            yield (ek + ej) + ei, ek + (ej + ei)
