from pydantic import BaseModel

from .mixins import (
    IDMixin,
    OrmModeMixin,
    UserIDMixin
)


__all__ = [
    'TagInCreate',
    'TagInUpdate',
    'TagInResponse'
]


class _TagBase(BaseModel):
    title: str
    description: str


class TagInCreate(_TagBase):
    pass


class TagInUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class TagInResponse(OrmModeMixin, UserIDMixin, IDMixin, _TagBase):
    user_id: int
