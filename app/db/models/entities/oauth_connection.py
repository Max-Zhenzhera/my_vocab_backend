from sqlalchemy import (
    Column,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped

from ..base import Base
from ..mixins import TimestampMixin
from ..mixins.user import UserMixin
from ...enums import OAuthBackend


__all__ = ['OAuthConnection']


class OAuthConnection(
    TimestampMixin,
    UserMixin,
    Base
):
    __tablename__ = 'oauth_connections'
    __table_args__ = (
        PrimaryKeyConstraint('oauth_id', 'backend'),
        UniqueConstraint('user_id', 'backend')
    )

    oauth_id: Mapped[str] = Column(
        String(64),
        nullable=False
    )
    backend: Mapped[OAuthBackend] = Column(
        ENUM(OAuthBackend, name='oauth_backend'),
        nullable=False
    )
    email: Mapped[str] = Column(
        String(256),
        nullable=False
    )
    detail: Mapped[str] = Column(
        String(256),
        nullable=False
    )
    """ Nickname, Full name or at least email of connected OAuth user."""

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'oauth_id={self.oauth_id!r}, '
            f'backend={self.backend!r}, '
            f'user_id={self.user_id!r}'
            ')'
        )
