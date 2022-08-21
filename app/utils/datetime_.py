import time
from datetime import (
    datetime,
    timedelta
)
from typing import (
    Literal,
    overload
)


__all__ = ['compute_expire']


@overload
def compute_expire(
    expire_in_seconds: int,
    *,
    as_int: Literal[False] = False
) -> datetime:
    ...


@overload
def compute_expire(
    expire_in_seconds: int,
    *,
    as_int: Literal[True]
) -> int:
    ...


def compute_expire(
    expire_in_seconds: int,
    *,
    as_int: bool = False
) -> int | datetime:
    if as_int:
        return _compute_expire_as_int(expire_in_seconds)
    return _compute_expire_as_datetime(expire_in_seconds)


def _compute_expire_as_int(expire_in_seconds: int) -> int:
    return int(time.time()) + expire_in_seconds


def _compute_expire_as_datetime(expire_in_seconds: int) -> datetime:
    return (
        datetime.utcnow()
        + timedelta(seconds=expire_in_seconds)
    )
