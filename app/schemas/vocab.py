from pydantic import BaseModel

from .mixins import (
    IDMixin,
    OrmModeMixin,
    UserIDMixin
)


__all__ = [
    'VocabInCreate',
    'VocabInUpdate',
    'VocabInResponse'
]


class _VocabBase(BaseModel):
    title: str
    description: str
    is_public: bool
    is_favourite: bool


class VocabInCreate(_VocabBase):
    pass


class VocabInUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_favourite: bool | None = None


class VocabInResponse(OrmModeMixin, UserIDMixin, IDMixin, _VocabBase):
    pass
