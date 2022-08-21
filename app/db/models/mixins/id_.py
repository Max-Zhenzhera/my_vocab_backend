from sqlalchemy import (
    BigInteger,
    Column
)
from sqlalchemy.orm import (
    Mapped,
    declarative_mixin,
    declared_attr
)


__all__ = ['IDMixin']


@declarative_mixin
class IDMixin:
    @declared_attr
    def id(self) -> Mapped[int]:
        return Column(
            BigInteger,
            primary_key=True
        )
