from dataclasses import dataclass
from typing import Any, Optional, List

from algebra.polynomial.multi_variable import MultiVariableElement, Monomial


@dataclass
class IdealGen:
    lead_monomial: Monomial
    element: MultiVariableElement
    right: Any

    def __lt__(self, other):
        return self.lead_monomial < other.lead_monomial


class Ideal:
    def __init__(self):
        self.generator: List[IdealGen] = []

    def represent(self, element: MultiVariableElement, right):
        for gen in self.generator:
            if (co := element[gen.lead_monomial]) != 0:
                element -= gen.element * co
                right -= gen.right * co

        return element, right

    def add(self, element: MultiVariableElement, right) -> Optional[IdealGen]:
        element, right = self.represent(element, right)
        if element != 0:
            lm = element.lead_monomial()
            lc = element.lead_coefficient()
            ig = IdealGen(
                lead_monomial=lm,
                element=element / lc,
                right=right / lc
            )
            self.generator.append(ig)
            self.generator.sort(reverse=True)
            return ig
        else:
            return IdealGen(
                lead_monomial=element.lead_monomial(),
                element=element,
                right=right
            )
