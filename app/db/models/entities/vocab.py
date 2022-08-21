from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    String,
    UniqueConstraint,
    false
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
    from .tag import Tag
    from .word import Word

__all__ = ['Vocab']


class Vocab(
    TimestampMixin,
    UserMixin,
    IDMixin,
    Base
):
    """
    `Vocab` - short form of the `vocabulary`.
    """

    __tablename__ = 'vocabs'
    __table_args__ = (
        UniqueConstraint('title', 'user_id'),
    )

    title: Mapped[str] = Column(
        String(128),
        nullable=False
    )
    description: Mapped[str] = Column(
        String(512),
        nullable=False
    )
    is_public: Mapped[bool] = Column(
        Boolean,
        nullable=False
    )
    is_favourite: Mapped[bool] = Column(
        Boolean,
        server_default=false(), nullable=False
    )

    tags: Mapped[list['Tag']] = relationship(
        'VocabTagAssociation',
        back_populates='vocab'
    )
    words: Mapped[list['Word']] = relationship(
        'Word',
        back_populates='vocab', passive_deletes=True
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'title={self.title!r}, '
            f'user_id={self.user_id!r}'
            ')'
        )
