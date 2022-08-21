from dataclasses import dataclass
from typing import (
    Any,
    Type,
    TypeVar
)

import pytest

from app.utils.casts import to_dataclass


T = TypeVar('T')


@dataclass
class Dataclass:
    var_1: int
    var_2: str
    var_3: bool


VAR_1 = 1
VAR_2 = 'string'
VAR_3 = True


class SomeObject:
    var_1: int = VAR_1
    var_2: str = VAR_2
    var_3: bool = VAR_3

    other_field: str = 'I do not needed!'


some_dict = {
    'var_1': VAR_1,
    'var_2': VAR_2,
    'var_3': VAR_3,

    'other_field': 'I do not needed!'
}

expected_dataclass_instance = Dataclass(
    var_1=VAR_1,
    var_2=VAR_2,
    var_3=VAR_3
)


@pytest.mark.parametrize(
    ('cls', 'data', 'result'),
    (
        (Dataclass, SomeObject, expected_dataclass_instance),
        (Dataclass, SomeObject(), expected_dataclass_instance),
        (Dataclass, some_dict, expected_dataclass_instance),
    )
)
def test_result(cls: Type[T], data: Any, result: T):
    assert to_dataclass(cls, data) == result
