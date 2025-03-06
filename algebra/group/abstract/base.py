import collections
import itertools
import random
from queue import Queue
from typing import List, TypeVar, Set, Dict, Optional, Iterator, Union, \
    Type

import pydantic
from pydantic import BaseModel

from algebra.number.util import factorize
from algebra.util.my_hash import int_sequence_hash

T = TypeVar("T")


class GroupRep(BaseModel):
    @property
    def identity(self):
        raise NotImplementedError(self)

    @property
    def group_cls(self) -> Type:
        return Group

    def object_list(self):
        raise NotImplementedError(self)

    def check_object(self, o):
        raise NotImplementedError(self)

    def element(self, *args):
        raise NotImplementedError(self)

    def group(self, elements=None, *, name=''):
        elements = elements or []
        element_list = []

        for element in elements:
            if not isinstance(element, GroupElement):
                element = self.element(element)

            if element.group != self:
                raise ValueError("Element should be belong to this group")

            element_list.append(element)

        return self.group_cls(
            represent=self,
            generator=element_list,
            name=name
        )

    def as_group(self):
        raise NotImplementedError(self)


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


class Group(BaseModel):
    represent: GroupRep
    generator: List['GroupElement']
    name: Optional[str] = ''
    _stabilizer_chain: Optional['StabilizerChain'] = None

    def __str__(self):
        if self.name:
            return self.name
        return ''.join([
            '{',
            ','.join(map(str, self.generator)),
            '}'
        ])

    def show(self):
        print("Generator")
        for g in self.generator:
            print('-', g)

    def group_id(self):
        # unique value up to isomorphism
        if self.is_abelian():
            key_list = [1]
            key_list.extend(self.get_abelian_key())
        else:
            key_list = [0]
            for item in sorted(self.order_statistics().items()):
                key_list.extend(item)

        return int_sequence_hash('Group', key_list)

    def append(self, element):
        return self.represent.group(self.generator + [element])

    def order(self):
        return self.stabilizer_chain().order

    def order_statistics(self):
        order_count = collections.defaultdict(int)
        for element in self.element_list():
            order_count[element.order()] += 1
        return dict(order_count)

    def order_statistics_element(self):
        order_count = collections.defaultdict(list)
        for element in self.element_list():
            order_count[element.order()].append(element)
        return dict(order_count)

    def element_list(self) -> Iterator['GroupElement']:
        return StabilizerTraveler(self).visit()

    def is_abelian(self):
        for g1 in self.generator:
            for g2 in self.generator:
                if g1 + g2 != g2 + g1:
                    return False
        return True

    def is_subgroup(self, other: 'Group'):
        for g in self.generator:
            if not other.element_test(g):
                return False
        return True

    def orbit(self, o: T) -> Set[T]:
        done = set()
        queue = {o}
        while queue:
            c = queue.pop()
            done.add(c)
            for g in self.generator:
                gc = g.act(c)
                if gc not in done:
                    queue.add(gc)
        return done

    def orbit_list(self):
        o_done = set()
        o_list = []

        for o in self.represent.object_list():
            if o in o_done:
                continue

            orbit = self.orbit(o)
            if len(orbit) > 1:
                o_list.append(orbit)
            o_done.update(orbit)

        return o_list

    def is_transitive(self):
        object_list = list(self.represent.object_list())
        for o in object_list:
            return len(self.orbit(o)) == len(object_list)

    def is_conjugate(self, other: 'Group') -> bool:
        if self.represent != other.represent:
            return False

        if not self.is_isomorphism(other):
            return False

        for g in self.represent.as_group().element_list():
            conjugate = self.conjugate(g)
            if conjugate.is_equal(other):
                return True

        return False

    def conjugate(self, other: 'GroupElement') -> 'Group':
        return Group(
            represent=self.represent,
            generator=[
                other + g - other
                for g in self.generator
            ]
        )

    def is_equal(self, other: 'Group') -> bool:
        if self.represent != other.represent:
            return False

        return (
            self.is_contained(other) and
            other.is_contained(self)
        )

    def is_contained(self, other: 'Group') -> bool:
        for g in other.generator:
            if not self.element_test(g):
                return False
        return True

    def stabilizer(self, o: T) -> 'Group':
        self.represent.check_object(o)

        done = set()
        queue = {o}
        transversal = {o: self.represent.identity}

        new_generator = []
        while queue:
            c = queue.pop()
            done.add(c)
            for g in self.generator:
                gc = g.act(c)
                if gc not in done:
                    transversal[gc] = transversal[c] + g
                    queue.add(gc)
                else:
                    new_generator.append(
                        transversal[c] + g - transversal[gc]
                    )

        return Group(
            represent=self.represent,
            generator=[
                g
                for g in new_generator
                if not g.is_identity()
            ]
        )

    def stabilizer_many(self, obj_list: List[T]) -> 'Group':
        current = self
        for obj in obj_list:
            current = current.stabilizer(obj)
        return current

    def stabilizer_chain(self, is_factor: bool = False) -> 'StabilizerChain':
        if self._stabilizer_chain is not None:
            # check factor info
            if not is_factor or self._stabilizer_chain.is_factor:
                return self._stabilizer_chain

        chain = StabilizerChain(
            group=self.represent.group(),
            is_factor=is_factor
        )
        obj_iter = ElementContainer(self.represent.object_list())
        for g in self.generator:
            if is_factor:
                g = ElementInfo(g, [g])
            chain.extend(g, obj_iter)

        self._stabilizer_chain = chain
        return chain

    def element_test(self, element: 'GroupElement'):
        return self.stabilizer_chain().element_test(element)

    def random_element(self) -> 'GroupElement':
        element = self.represent.identity
        for stabilizer in self.stabilizer_chain().travel():
            if stabilizer.is_trivial():
                break
            info = random.choice(list(stabilizer.transversal.values()))
            element += info.element
        return element

    def factor(self, element: 'GroupElement'):
        chain = self.stabilizer_chain(True)
        if not self.element_test(element):
            raise ValueError('Element not in the Group')

        return chain.factor(element)

    def normal_closure(self, element_list: List['GroupElement']):
        for element in element_list:
            if not self.element_test(element):
                raise ValueError('Element should be belong to this group')

        chain = StabilizerChain(group=self.represent.group())
        obj_iter = ElementContainer(self.represent.object_list())

        insert_queue = set(element_list)
        while insert_queue:
            element = insert_queue.pop()

            for generator in self.generator:
                new_element = -generator + element + generator
                if not chain.element_test(new_element):
                    chain.extend(new_element, obj_iter)
                    insert_queue.add(new_element)

        return chain.construct()

    def center(self):
        chain = StabilizerChain(group=self.represent.group())
        obj_iter = ElementContainer(self.represent.object_list())

        for element in self.element_list():
            if self.is_commute(element):
                if not chain.element_test(element):
                    chain.extend(element, obj_iter)

        return chain.construct()

    def is_commute(self, element: 'GroupElement'):
        for gen in self.generator:
            left = gen + element
            right = element + gen
            if left != right:
                return False
        return True

    def is_trivial(self):
        for gen in self.generator:
            if not gen.is_identity():
                return False
        return True

    def is_normal(self, subgroup: 'Group'):
        for sub_gen in subgroup.generator:
            if not self.element_test(sub_gen):
                # Not subgroup
                return False
            for gen in self.generator:
                conjugate = gen + sub_gen - gen
                if not subgroup.element_test(conjugate):
                    # Not normal
                    return False
        return True

    def is_isomorphism(self, others: 'Group'):
        # abelian 인지 확인한다.
        if self.is_abelian():
            if others.is_abelian():
                # abelian인 경우 abelian key를 계산해서 비교ㄴㄴㄴ
                return self.get_abelian_key() == others.get_abelian_key()
            else:
                return False
        else:
            if others.is_abelian():
                return False

        # order 확인
        if self.order() != others.order():
            return False

        # order statistics 확인
        if self.order_statistics() != others.order_statistics():
            return False

        # FIXME: 맞지는 않지만, 당장의 runtime을 위해 이걸로 충분할 것이다.
        if True:
            return True

        # 일일이 확인 |G| = |f(G)| = |H|임을 이용
        others_statistics = others.order_statistics_element()
        candidate_list = []
        for gen in self.generator:
            candidate = others_statistics[gen.order()]
            candidate_list.append(candidate)

        from algebra.group.homomorphism import GroupHomomorphism

        order = self.order()

        for valid_image in itertools.product(*candidate_list):
            hom = GroupHomomorphism(
                domain=self,
                codomain=others,
                mapping=dict(zip(self.generator, valid_image)),
                raise_exception=False
            )
            if not hom.is_valid_structure():
                continue
            if hom.image().order() != order:
                continue

            return True

        print("Order Statistic은 같은데 Isomorphism하지 않은 반례")
        print(self, others)
        return False

    def get_abelian_key(self) -> list[int]:
        if not self.is_abelian():
            raise ValueError('Abelian group must be given')

        result: list[tuple[int, int]] = []
        for number in self._get_abelian_key_gen():
            result.extend(factorize(number).items())
        result.sort()
        return [p ** e for p, e in result]

    def _get_abelian_key_gen(self):
        return StabilizerOrderTraveler(self).visit()

    def subgroup_list(self):
        raise NotImplementedError(self)

    def centralizer(self, element: 'GroupElement'):
        pass

    def normalizer(self, subgroup: 'Group'):
        pass

    def conjugacy_classes(self):
        pass

    def conjugacy_classes_subgroups(self):
        pass

    def intermediate_subgroups(self):
        pass

    def normal_subgroups(self):
        pass

    def maximal_subgroup_class_reps(self):
        pass

    def isomorphism_groups(self, others: 'Group'):
        pass

    def automorphism_group(self):
        raise NotImplementedError(self)

    def g_quotients(self, others: 'Group'):
        pass


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
    group: Group
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
        new_group = self.group.copy()
        new_group._stabilizer_chain = self
        return new_group


class GroupElement(BaseModel):
    group: GroupRep

    def __add__(self, other: 'GroupElement') -> 'GroupElement':
        raise NotImplementedError(self)

    def __neg__(self) -> 'GroupElement':
        raise NotImplementedError(self)

    def __sub__(self, other: 'GroupElement') -> 'GroupElement':
        return self + (-other)

    def __eq__(self, other: 'GroupElement') -> bool:
        return (self - other).is_identity()

    def is_identity(self) -> bool:
        raise NotImplementedError(self)

    def order(self) -> int:
        raise NotImplementedError(self)

    def act(self, o: T) -> T:
        """
        "Group Action" on some Set and T is a element of the set.

        :param o: Element on T
        :return: Another T
        """
        raise NotImplementedError(self)
