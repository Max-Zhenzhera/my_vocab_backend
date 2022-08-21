from dataclasses import dataclass

from app.dtos.oauth import OAuthUser
from app.schemas.user import (
    UserInCreate,
    UserInLogin,
    UserInOAuthCreate
)


__all__ = ['MetaUser']


@dataclass
class MetaUser:
    email: str
    username: str
    password: str
    oauth_id: str

    @property
    def in_create(self) -> UserInCreate:
        return UserInCreate(
            email=self.email,
            username=self.username,
            password=self.password
        )

    @property
    def in_oauth_create(self) -> UserInOAuthCreate:
        return UserInOAuthCreate(
            username=self.username,
            password=self.password
        )

    @property
    def in_login(self) -> UserInLogin:
        return UserInLogin(
            email=self.email,
            password=self.password
        )

    @property
    def oauth(self) -> OAuthUser:
        return OAuthUser(
            id=self.oauth_id,
            email=self.email,
            detail=self.username
        )
