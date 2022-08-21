from typing import Any

from sqlalchemy import (
    Column,
    ForeignKey
)
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import (
    Mapped,
    declarative_mixin,
    declared_attr,
    relationship
)

from ..entities.user import User
from ...constants import CASCADE


__all__ = ['UserMixin']


@declarative_mixin
class UserMixin:
    @declared_attr
    def user_id(self) -> Mapped[int]:
        return Column(
            ForeignKey('users.id', ondelete=CASCADE),
            nullable=False
        )

    @declared_attr
    def user(self) -> Mapped[User]:
        return relationship('User')

    @hybrid_method
    def is_owner(self, user_id: int) -> Any:
        return self.user_id == user_id
