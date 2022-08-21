from pydantic import (
    BaseModel,
    EmailStr,
    Field
)

from .mixins import (
    IDMixin,
    OrmModeMixin
)
from .re_ import USERNAME_REGEX


__all__ = [
    'UserInCreate',
    'UserInOAuthCreate',
    'UserInLogin',
    'UserInResponse'
]


class _EmailFieldMixin(BaseModel):
    email: EmailStr


class _UsernameFieldMixin(BaseModel):
    username: str = Field(regex=USERNAME_REGEX)


class _PasswordFieldMixin(BaseModel):
    password: str


class _UserBase(_UsernameFieldMixin, _EmailFieldMixin):
    pass


class UserInCreate(_PasswordFieldMixin, _UserBase):
    pass


class UserInOAuthCreate(_PasswordFieldMixin, _UsernameFieldMixin):
    pass


class UserInLogin(_PasswordFieldMixin, _EmailFieldMixin):
    pass


class UserInResponse(OrmModeMixin, IDMixin, _UserBase):
    is_active: bool
    is_superuser: bool
