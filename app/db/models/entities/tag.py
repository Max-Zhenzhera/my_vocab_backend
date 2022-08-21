from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    String,
    UniqueConstraint
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
from ..mixins.user import UserMixin


if TYPE_CHECKING:
    from .vocab import Vocab

__all__ = ['Tag']


class Tag(
    TimestampMixin,
    UserMixin,
    IDMixin,
    Base
):
    __tablename__ = 'tags'
    __table_args__ = (
        UniqueConstraint('title', 'user_id'),
    )

    title = Column(
        String(64),
        nullable=False
    )
    description: Mapped[str] = Column(
        String(256),
        nullable=False
    )

    vocabs: Mapped[list['Vocab']] = relationship(
        'VocabTagAssociation',
        back_populates='tag'
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'title={self.title!r} ,'
            f'user_id={self.user_id!r}'
            ')'
        )
