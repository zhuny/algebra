import collections
from fractions import Fraction
from typing import Any


def remove_zero_dict(dict_object: dict[Any, Any]) -> dict[Any, Any]:
    return {
        key: value
        for key, value in dict_object.items()
        if value != 0
    }
