from sqlalchemy import (
    Column,
    String
)
from sqlalchemy.dialects.postgresql import (
    INET,
    UUID
)
from sqlalchemy.orm import Mapped

from ..base import Base
from ..mixins import (
    ExpirableMixin,
    IDMixin,
    TimestampMixin
)
from ..mixins.user import UserMixin
from ...functions.server_defaults import gen_random_uuid


__all__ = ['RefreshSession']


class RefreshSession(
    TimestampMixin,
    ExpirableMixin,
    UserMixin,
    IDMixin,
    Base
):
    __tablename__ = 'refresh_sessions'

    refresh_token: Mapped[str] = Column(
        UUID,
        unique=True, index=True, server_default=gen_random_uuid()
    )
    access_token: Mapped[str] = Column(
        String,
        nullable=False
    )
    ip_address: Mapped[str] = Column(
        INET,
        nullable=False
    )
    user_agent: Mapped[str] = Column(
        String(256),
        nullable=False
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'refresh_token={self.refresh_token!r}, '
            f'access_token={self.access_token!r}, '
            f'expires_at={self.expires_at!r}, '
            f'user_id={self.user_id!r}'
            ')'
        )
