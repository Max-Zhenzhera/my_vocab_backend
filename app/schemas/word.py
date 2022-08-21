from pydantic import BaseModel

from .mixins import (
    IDMixin,
    OrmModeMixin,
    UserIDMixin
)


__all__ = [
    'WordInCreate',
    'WordInUpdate',
    'WordInResponse'
]


class _WordBase(BaseModel):
    word: str
    is_learned: bool
    is_marked: bool
    vocab_id: int


class WordInCreate(_WordBase):
    pass


class WordInUpdate(BaseModel):
    word: str | None = None
    is_learned: bool | None = None
    is_marked: bool | None = None
    vocab_id: int | None = None


class WordInResponse(OrmModeMixin, UserIDMixin, IDMixin, _WordBase):
    pass
