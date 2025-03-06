from algebra.util.model import AlgebraModelBase


class MonomialOrderingBase(AlgebraModelBase):
    def key(self, monomial):
        raise NotImplementedError()


class LexicographicMonomialOrdering(MonomialOrderingBase):
    def key(self, monomial):
        return monomial.power


class GradedLexicographicOrdering(MonomialOrderingBase):
    def key(self, monomial):
        total_degree = sum(monomial.power)
        return [total_degree] + monomial.power


class GradedReverseLexicographicOrdering(MonomialOrderingBase):
    def key(self, monomial):
        total_degree = sum(monomial.power)
        power = [-d for d in monomial.power]
        power.reverse()
        return [total_degree] + power
