from dataclasses import dataclass

from fastapi import Depends

from .errors import OAuthConnectionDoesNotExistError
from .mixins import CtxOAuthBackendMixin
from ..auth import (
    Authenticator,
    AuthService
)
from ..auth.base import BaseAuthService
from ...db.errors import EntityDoesNotExistError
from ...db.models import OAuthConnection
from ...db.repos import OAuthConnectionsRepo
from ...dtos.oauth import OAuthUser
from ...schemas.auth import AuthResult
from ...schemas.user import (
    UserInCreate,
    UserInOAuthCreate
)


__all__ = ['OAuthService']


@dataclass
class OAuthService(CtxOAuthBackendMixin, BaseAuthService):
    service: AuthService = Depends()
    repo: OAuthConnectionsRepo = Depends()

    @property
    def authenticator(self) -> Authenticator:
        return self.service.authenticator

    async def register(  # type: ignore[override]
        self,
        oauth_user: OAuthUser,
        payload: UserInOAuthCreate
    ) -> AuthResult:
        user_in_create = self._form_user_in_create(oauth_user, payload)
        auth_result = await self.service.register(user_in_create)
        await self.link(oauth_user, auth_result.user.id)
        return auth_result

    @staticmethod
    def _form_user_in_create(
        oauth_user: OAuthUser,
        user_in_oauth_create: UserInOAuthCreate
    ) -> UserInCreate:
        return UserInCreate(
            email=oauth_user.email,
            username=user_in_oauth_create.username,
            password=user_in_oauth_create.password
        )

    async def link(
        self,
        oauth_user: OAuthUser,
        internal_user_id: int
    ) -> OAuthConnection:
        return await self.repo.link(
            oauth_user=oauth_user,
            internal_user_id=internal_user_id,
            backend=self.backend
        )

    async def login(  # type: ignore[override]
        self,
        oauth_user: OAuthUser
    ) -> AuthResult:
        connection = await self._get_oauth_connection(oauth_user.id)
        return await self.authenticator.authenticate(connection.user)

    async def _get_oauth_connection(
        self,
        oauth_id: str
    ) -> OAuthConnection:
        try:
            connection = await self.repo.get_one_by_pk(
                [oauth_id, self.backend],
                [OAuthConnection.user]
            )
        except EntityDoesNotExistError as error:
            raise OAuthConnectionDoesNotExistError from error
        else:
            return connection
