import collections
import itertools
from typing import List, Set, Optional, Iterator, Type

from pydantic import BaseModel

from algebra.number.util import factorize
from algebra.util.my_hash import int_sequence_hash


class GroupRep(BaseModel):
    @property
    def identity(self):
        raise NotImplementedError(type(self))

    @property
    def group_cls(self) -> Type:
        raise NotImplementedError(type(self))

    @property
    def element_cls(self) -> Type:
        raise NotImplementedError(type(self))

    def element(self, *args, **kwargs):
        # you may need to override this function
        return self.element_cls(*args, **kwargs)

    def group(self, elements=None, *, name=''):
        elements = elements or []
        element_list = []

        for element in elements:
            if not isinstance(element, GroupElement):
                element = self.element(element)

            if element.represent != self:
                raise ValueError("Element should be belong to this group")

            element_list.append(element)

        return self.group_cls(
            represent=self,
            generator=element_list,
            name=name
        )

    def as_group(self):
        raise NotImplementedError(type(self))


# generic을 받아서 GroupElement를 받을 수 있도록 하자
class Group(BaseModel):
    represent: GroupRep
    generator: List['GroupElement']
    name: Optional[str] = ''

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

    def group_copy(self):
        return self.represent.group(elements=self.generator)

    def append(self, element):
        return self.represent.group(self.generator + [element])

    def order(self):
        raise NotImplementedError(type(self))

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
        raise NotImplementedError(type(self))

    def is_abelian(self):
        for g1 in self.generator:
            for g2 in self.generator:
                if g1 + g2 != g2 + g1:
                    return False
        return True

    def is_subgroup(self, other: 'Group'):
        if self.represent != other.represent:
            return False

        for g in self.generator:
            if not other.element_test(g):
                return False
        return True

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
            self.is_subgroup(other) and
            other.is_subgroup(self)
        )

    def element_test(self, element: 'GroupElement'):
        raise NotImplementedError(type(self))

    def random_element(self) -> 'GroupElement':
        raise NotImplementedError(type(self))

    def factor(self, element: 'GroupElement'):
        raise NotImplementedError(type(self))

    def normal_closure(self, element_list: List['GroupElement']):
        raise NotImplementedError(type(self))

    def center(self):
        raise NotImplementedError(type(self))

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
        raise NotImplementedError(type(self))

    def subgroup_list(self):
        raise NotImplementedError(type(self))

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
        raise NotImplementedError(type(self))

    def g_quotients(self, others: 'Group'):
        pass

    def stabilize_pair(self, rep: GroupRep, pair_list: list['GroupElementPair']):
        raise NotImplementedError(type(self))


class GroupElement(BaseModel):
    represent: GroupRep

    def __add__(self, other: 'GroupElement') -> 'GroupElement':
        raise NotImplementedError(type(self))

    def __neg__(self) -> 'GroupElement':
        raise NotImplementedError(type(self))

    def __sub__(self, other: 'GroupElement') -> 'GroupElement':
        return self + (-other)

    def __eq__(self, other: 'GroupElement') -> bool:
        return (self - other).is_identity()

    def is_identity(self) -> bool:
        raise NotImplementedError(type(self))

    def order(self) -> int:
        # 만약 더 빠른 알고리즘이 있다면 각 class에서 구현
        return self.represent.group([self]).order()


class GroupElementPair(BaseModel):
    # act as pair temporary

    source: GroupElement
    target: GroupElement

    def __str__(self):
        return f'Pair(source={self.source}, target={self.target})'

    def __add__(self, other):
        return GroupElementPair(
            source=self.source + other.source,
            target=self.target + other.target
        )

    def __sub__(self, other):
        return GroupElementPair(
            source=self.source - other.source,
            target=self.target - other.target
        )

    def __neg__(self):
        return GroupElementPair(source=-self.source, target=-self.target)

    def is_identity(self) -> bool:
        return self.source.is_identity() and self.target.is_identity()
