from pydantic import (
    BaseConfig,
    BaseModel
)


__all__ = [
    'IDMixin',
    'UserIDMixin',
    'OrmModeMixin'
]


class IDMixin(BaseModel):
    id: int


class UserIDMixin(BaseModel):
    user_id: int


class OrmModeMixin(BaseModel):
    class Config(BaseConfig):
        orm_mode = True
