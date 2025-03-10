import collections
from queue import Queue
from typing import Optional, List, Dict, Union, TypeVar

import pydantic
from pydantic import BaseModel

from algebra.group.abstract.base import Group, GroupElement
from algebra.group.abstract.permutation.base import PermutationGroup

T = TypeVar('T')


class StabilizerTraveler:
    def __init__(self, group):
        self.group: Group = group

    def visit(self):
        stack = [(
            self.group.stabilizer_chain(),
            self.group.represent.identity
        )]

        while stack:
            chain, element = stack.pop()
            chain: StabilizerChain
            element: GroupElement
            if chain.is_trivial():
                yield element
            else:
                for t in chain.transversal.values():
                    stack.append((
                        chain.stabilizer,
                        t.element + element
                    ))


class StabilizerOrderTraveler:
    def __init__(self, group):
        self.group: Group = group

    def visit(self):
        current_group = self.group.represent.group()

        for stabilizer in self.group.stabilizer_chain().travel():
            order = len(stabilizer.transversal)
            if order == 0:
                break

            orbit_set = {stabilizer.point}
            for g in stabilizer.transversal.values():
                if self._is_run_needed(orbit_set, g.element):
                    for o in list(orbit_set):
                        orbit_set.update(g.element.orbit(o))

                    before_order = current_group.order()
                    current_group = current_group.append(g.element)
                    after_order = current_group.order()

                    yield after_order // before_order

    def _is_run_needed(self, orbit_set, g):
        for o in orbit_set:
            return g.act(o) not in orbit_set


class ElementContainer:
    def __init__(self, element_list):
        self.element_set = set(element_list)
        self.element_iter = self.iter_repeat()
        self.element_used = set()

    def iter_repeat(self):
        while True:
            for element in self.element_set:
                yield element

    def get_next(self, group_element: 'GroupElement'):
        for element in self.element_iter:
            if element in self.element_used:
                continue

            acted_element = group_element.act(element)
            if acted_element != element:
                self.element_used.add(element)
                return element


class ElementInfo(BaseModel):
    element: 'GroupElement'
    factor: Optional[List['GroupElement']] = None

    def __add__(self, other):
        if not isinstance(other, ElementInfo):
            raise TypeError('ElementInfo is required')

        element = self.element + other.element
        if self.factor is None or other.factor is None:
            factor = None
        else:
            factor = self._normalize_factor(self.factor + other.factor)

        return ElementInfo(element=element, factor=factor)

    def __sub__(self, other):
        if not isinstance(other, ElementInfo):
            raise TypeError('ElementInfo is required')

        return self + (-other)

    def __neg__(self):
        if self.factor is None:
            factor = None
        else:
            factor = [-f for f in self.factor]
            factor.reverse()

        return ElementInfo(element=-self.element, factor=factor)

    def show(self):
        print(self.element)
        if self.factor is not None:
            for factor in self.factor:
                print('-', factor)
            print('-', len(self.factor))

    def length(self):
        return len(self.factor) if self.factor else 0

    def _normalize_factor(self, factor_list):
        factor_count = []

        for factor in factor_list:
            if factor_count and (factor_count[-1][0] - factor).is_identity():
                factor_count[-1][1] += 1
            elif factor_count and (factor_count[-1][0] + factor).is_identity():
                factor_count[-1][1] -= 1
            else:
                factor_count.append([factor, 1])
            if factor_count[-1][1] == 0:
                factor_count.pop()

        factor_result = []
        for factor, count in factor_count:
            order_it = count % factor.order()
            order_left = -count % factor.order()

            if order_it > order_left:
                order_it = order_left
                factor = -factor
            factor_result.extend([factor] * order_it)
        return factor_result


class StabilizerChain(BaseModel):
    group: PermutationGroup
    point: T = None
    transversal: Dict[T, ElementInfo] = pydantic.Field(default_factory=dict)
    generator_factor: Dict['GroupElement', ElementInfo] = pydantic.Field(
        default_factory=dict
    )
    stabilizer: Optional['StabilizerChain'] = None
    depth: int = 0
    is_factor: bool = False

    @property
    def order(self):
        if self.is_trivial():
            return 1
        else:
            return len(self.transversal) * self.stabilizer.order

    def is_trivial(self):
        return self.point is None

    def travel(self):
        current = self
        yield current
        while not current.is_trivial():
            current = current.stabilizer
            yield current

    def element_test(self, element: 'GroupElement'):
        if element.is_identity():
            return True

        for stabilizer in self.travel():
            if stabilizer.point is None:
                return element.is_identity()

            base = element.act(stabilizer.point)
            if base not in stabilizer.transversal:
                return False

            t = stabilizer.transversal[base]
            element -= t.element

        # Unreachable
        return True

    def factor(self, element: 'GroupElement') -> List['GroupElement']:
        if element.is_identity():
            return []

        factor_info = ElementInfo(
            self.group.represent.identity,
            []
        )

        for stabilizer in self.travel():
            if stabilizer.point is None:
                break

            base = element.act(stabilizer.point)
            info = stabilizer.transversal[base]
            element -= info.element
            factor_info += info

        return factor_info.factor

    def show(self):
        for stack in self.travel():
            print(f"=== STACK-{stack.depth} ===")
            print(f"Fixed Point : {stack.point}")
            print("Transversal")
            for k, t in stack.transversal.items():
                print(f"  - {k} : {t.element}")
            print("Group Generator")
            for g in stack.group.generator:
                print(f"  - {g}")
            print()

    def extend(self,
               alpha: Union[ElementInfo, 'GroupElement'],
               next_object: ElementContainer):
        """
        :param alpha: Inserted element
        :param next_object: Object for permutation
        :return:
        """
        if isinstance(alpha, GroupElement):
            alpha = ElementInfo(element=alpha)

        # It is implementation of Schreier-Sims algorithm
        if not self.element_test(alpha.element):
            # Extend existing stabilizer chain
            if self.is_trivial():  # we are on the bottom of the chain
                self.group.generator.append(alpha.element)
                self.generator_factor[alpha.element] = alpha

                # pick random object from base point
                beta = self.point = next_object.get_next(alpha.element)
                self.stabilizer = StabilizerChain(  # Add a new layer
                    group=self.group.represent.group(),
                    depth=self.depth + 1,
                    is_factor=self.is_factor
                )
                self.transversal[beta] = ElementInfo(
                    element=self.group.represent.identity,
                    factor=[] if self.is_factor else None
                )

                delta = alpha.element.act(beta)
                s = alpha  # orbit algorithm for single generator group

                while delta != beta:
                    self.transversal[delta] = s
                    delta, s = alpha.element.act(delta), s + alpha

                self.stabilizer.extend(s, next_object)  # remove recursive
            else:
                queue = Queue()
                for delta, transversal in self.transversal.items():
                    queue.put((delta, transversal, False))

                new_orbit = collections.defaultdict(list)

                while queue.qsize() > 0:
                    delta, transversal, is_new = queue.get()
                    check_element = [alpha]
                    if is_new:
                        for generator in self.generator_factor.values():
                            check_element.append(generator)
                            check_element.append(-generator)

                    for element in check_element:
                        gamma = element.element.act(delta)
                        new_element = transversal + element

                        if gamma not in self.transversal:
                            if gamma not in new_orbit:
                                queue.put((gamma, new_element, True))
                            new_orbit[gamma].append(new_element)
                        else:
                            self.stabilizer.extend(
                                new_element - self.transversal[gamma],
                                next_object
                            )

                for gamma, new_element_list in new_orbit.items():
                    new_element = min(
                        new_element_list,
                        key=lambda e: e.length()
                    )
                    self.transversal[gamma] = new_element
                    for another_element in new_element_list:
                        if new_element == another_element:
                            continue
                        self.stabilizer.extend(
                            another_element - new_element,
                            next_object
                        )

                self.group.generator.append(alpha.element)
                self.generator_factor[alpha.element] = alpha

    def construct(self):
        new_group = self.group.group_copy()
        new_group._stabilizer_chain = self
        return new_group
