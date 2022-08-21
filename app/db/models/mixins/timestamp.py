from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime
)
from sqlalchemy.orm import (
    Mapped,
    declarative_mixin,
    declared_attr
)

from ...functions.server_defaults import utcnow


__all__ = [
    'CreatedAtMixin',
    'UpdatedAtMixin',
    'TimestampMixin'
]


@declarative_mixin
class CreatedAtMixin:
    @declared_attr
    def created_at(self) -> Mapped[datetime]:
        return Column(
            DateTime,
            server_default=utcnow(), nullable=False
        )


@declarative_mixin
class UpdatedAtMixin:
    @declared_attr
    def updated_at(self) -> Mapped[datetime]:
        return Column(
            DateTime,
            onupdate=utcnow()
        )


@declarative_mixin
class TimestampMixin(UpdatedAtMixin, CreatedAtMixin):
    pass
