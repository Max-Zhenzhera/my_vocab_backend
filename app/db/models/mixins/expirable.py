from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    Mapped,
    declarative_mixin,
    declared_attr
)


__all__ = ['ExpirableMixin']


@declarative_mixin
class ExpirableMixin:
    @declared_attr
    def expires_at(self) -> Mapped[datetime]:
        return Column(
            DateTime,
            nullable=False
        )

    @hybrid_property
    def is_expired(self) -> bool:
        return self.expires_at < datetime.utcnow()
