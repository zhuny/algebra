from queue import Queue
from typing import TypeVar, Optional

from pydantic import ConfigDict
from typing_extensions import Generic

from algebra2.exception import Unreachable
from algebra2.group.base import AppBaseModel
from algebra2.group.permutation.base import PermutationGroupRepresentation, PermutationGroupElement, \
    PermutationGroupDefinition, PermutationGroupObject

# 앞으로 나올 4개를 서로 묶을 타입 변수
R = TypeVar("R", bound=PermutationGroupRepresentation)  # representation 타입
E = TypeVar("E", bound=PermutationGroupElement)         # element 타입
G = TypeVar("G", bound=PermutationGroupDefinition)      # group 타입
O = TypeVar("O", bound=PermutationGroupObject)          # object 타입


class StabilizerChainLayer(AppBaseModel, Generic[R, E, G, O]):
    model_config = ConfigDict(frozen=False)

    object: O | None = None
    transversal: dict[O, E] = {}
    generator: list[E] = []
    stabilizer: Optional['StabilizerChainLayer[R, E, G, O]'] = None

    def extend(self, element: E, obj_iter: 'ObjectContainer[E, O]'):
        if self.contains(element):
            return

        if self.is_leaf():
            # object확인해서 필요한 만큼만 layer를 생성한다.
            beta = obj_iter.get_next(element)
            if beta is None:
                return

            # Add new layer
            self.object = beta
            self.generator.append(element)
            self.stabilizer = StabilizerChainLayer()
            self.transversal[beta] = element.representation.identity()

            delta = element.act(beta)
            s = element

            while delta != beta:
                self.transversal[delta] = s
                delta = element.act(delta)
                s *= element

            self.stabilizer.extend(s, obj_iter)
            return

        # trivial 하지 않은 경우 각 원소들에 대해서 traversal을 업데이트
        queue = Queue()
        for delta, transversal in self.transversal.items():
            queue.put((delta, transversal, False))

        while queue.qsize() > 0:
            delta, transversal, is_new = queue.get()
            check_element_list = [element]
            if is_new:
                check_element_list.extend(self.generator)

            for current_element in check_element_list:
                gamma = current_element.act(delta)
                if gamma in self.transversal:
                    self.stabilizer.extend(
                        transversal * current_element / self.transversal[gamma],
                        obj_iter
                    )
                else:
                    self.transversal[gamma] = transversal * current_element
                    queue.put((gamma, self.transversal[gamma], True))

        self.generator.append(element)

    def contains(self, element: E) -> bool:
        if element.is_identity():
            return True

        for stabilizer in self.travel():
            if stabilizer.is_leaf():
                return element.is_identity()

            base = element.act(stabilizer.object)
            if base not in stabilizer.transversal:
                return False
            element /= stabilizer.transversal[base]

        raise Unreachable()

    def is_leaf(self):
        return self.object is None

    def travel(self):
        yield self

        current = self
        while not current.is_leaf():
            current = current.stabilizer
            yield current


class StabilizerChain(AppBaseModel, Generic[R, E, G, O]):
    representation: R
    top_layer: 'StabilizerChainLayer[R, E, G, O]'

    @classmethod
    def build(cls, group: G) -> 'StabilizerChain[R, E, G, O]':
        obj_iter = ObjectContainer(object_list=list(group.representation.iter_objects()))
        top_layer = StabilizerChainLayer()
        for g in group.generator_list:
            top_layer.extend(g, obj_iter)

        return StabilizerChain(
            representation=group.representation,
            top_layer=top_layer
        )

    def order(self) -> int:
        answer = 1
        for layer in self.top_layer.travel():
            if layer.is_leaf():
                break
            answer *= len(layer.transversal)
        return answer


class ObjectContainer(Generic[E, O]):
    def __init__(self, object_list: list[O]):
        self.object_list = object_list
        self.unused_object = set(object_list)
        self.used_object = set()

    def get_next(self, element: E) -> O | None:
        next_obj = self._get_next(element)
        if next_obj is not None:
            self.unused_object.remove(next_obj)
            self.used_object.add(next_obj)
            return next_obj

    def _get_next(self, element: E) -> O | None:
        # Act가 trivial하지 않은 obj 먼저
        for obj in self.unused_object:
            acted_obj = element.act(obj)
            if acted_obj != obj:
                return obj

        # 없는 경우 하나 먼저 고르기
        for obj in self.unused_object:
            return obj
