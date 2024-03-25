from algebra.group.abstract.base import Group


class SylowGroupCalculation:
    def __init__(self, group, prime):
        # TODO: check `prime` is prime number

        self.group: Group = group
        self.prime = prime

    def calculate(self):
        return self._calculate(self.group)

    def _calculate(self, group: Group):
        p = self.prime

        # if group is p-group, return itself
        if group.is_p_group(p):
            return group

        order = group.order()

        if order % p != 0:
            return group.represent.group()

        if order % (p * p) != 0:
            # Note that this function may fail
            g = self.find_p_element(group)
            if g is not None:
                return group.represent.group(g)

        # if not group.is_transitive():
        #     return self._calculate_intransitive(group)

        assert False

    def find_p_element(self, group):
        limit = group.order() // self.prime

        for i in range(limit):
            element = group.random_element()
            if (e_order := element.order()) % self.prime == 0:
                return element.pow(e_order // self.prime)

    def _calculate_intransitive(self, group):
        current_group = group
        for o_list in group.orbit_list():
            homomorphism = group.stabilizer_as_hom(o_list)
            current_group = homomorphism.inverse_group(
                self._calculate(
                    homomorphism.value_group(current_group)
                )
            )
            if current_group.is_p_group(self.prime):
                break

        return current_group
