from typing import Literal

from pydantic import BaseModel

from .mixins import OrmModeMixin
from .user import UserInResponse


__all__ = [
    'CredentialsInResponse',
    'AuthResult'
]


class CredentialsInResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: Literal['Bearer'] = 'Bearer'
    refresh_token: str


class AuthResult(OrmModeMixin):
    credentials: CredentialsInResponse
    user: UserInResponse
