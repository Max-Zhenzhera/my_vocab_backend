from dataclasses import fields
from operator import getitem
from typing import (
    Any,
    Callable,
    Type,
    TypeVar
)


__all__ = ['to_dataclass']


T = TypeVar('T')


def to_dataclass(cls: Type[T], data: Any) -> T:
    if isinstance(data, dict):
        return _to_dataclass(cls, getitem, data)
    return _to_dataclass(cls, getattr, data)


def _to_dataclass(
        cls: Type[T],
        handler: Callable[[Any, str], Any],
        data: Any
) -> T:
    parsed = {
        field.name: handler(data, field.name)
        for field in fields(cls)
    }
    return cls(**parsed)
