from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
    false,
    true
)
from sqlalchemy.orm import (
    Mapped,
    relationship
)

from ..base import Base
from ..mixins import (
    IDMixin,
    TimestampMixin
)


if TYPE_CHECKING:
    from .oauth_connection import OAuthConnection
    from .refresh_session import RefreshSession
    from .tag import Tag
    from .vocab import Vocab

__all__ = ['User']


class User(
    TimestampMixin,
    IDMixin,
    Base
):
    __tablename__ = 'users'

    email: Mapped[str] = Column(
        String(256),
        nullable=False, index=True, unique=True
    )
    username: Mapped[str] = Column(
        String(256),
        nullable=False, index=True, unique=True
    )
    hashed_password: Mapped[str] = Column(
        String(128),
        nullable=False
    )
    is_active: Mapped[bool] = Column(
        Boolean,
        server_default=true(), nullable=False
    )
    is_superuser: Mapped[bool] = Column(
        Boolean,
        server_default=false(), nullable=False
    )
    email_updated_at: Mapped[datetime] = Column(
        DateTime
    )

    tags: Mapped[list['Tag']] = relationship(
        'Tag',
        back_populates='user', passive_deletes=True
    )
    vocabs: Mapped[list['Vocab']] = relationship(
        'Vocab',
        back_populates='user', passive_deletes=True
    )
    refresh_sessions: Mapped[list['RefreshSession']] = relationship(
        'RefreshSession',
        back_populates='user', passive_deletes=True
    )
    oauth_connections: Mapped[list['OAuthConnection']] = relationship(
        'OAuthConnection',
        back_populates='user', passive_deletes=True
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'email={self.email!r}, '
            f'username={self.username!r}, '
            f'is_superuser={self.is_superuser!r}'
            ')'
        )
