import logging
from dataclasses import dataclass

from fastapi import Depends

from .authenticator import Authenticator
from .base import BaseServerAuthService
from .user import UserService
from ...schemas.auth import AuthResult
from ...schemas.user import (
    UserInCreate,
    UserInLogin
)


__all__ = ['AuthService']


logger = logging.getLogger(__name__)


@dataclass
class AuthService(BaseServerAuthService):
    user_service: UserService = Depends()
    authenticator: Authenticator = Depends()

    async def register(  # type: ignore[override]
        self,
        user_in_create: UserInCreate
    ) -> AuthResult:
        user = await self.user_service.create(user_in_create)
        return await self.authenticator.authenticate(user)

    async def login(  # type: ignore[override]
        self,
        user_in_login: UserInLogin
    ) -> AuthResult:
        user = await self.user_service.verify(user_in_login)
        return await self.authenticator.authenticate(user)

    async def refresh(  # type: ignore[override]
        self,
        token: str
    ) -> AuthResult:
        session = await self.authenticator.validate_refresh_session(token)
        await self.authenticator.blacklist_access_token(session.access_token)
        user = await self.user_service.repo.get_one_by_pk(session.user_id)
        return await self.authenticator.authenticate(user)
