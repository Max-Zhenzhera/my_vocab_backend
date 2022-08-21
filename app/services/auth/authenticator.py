import logging
from contextlib import suppress
from dataclasses import dataclass

from fastapi import Depends
from jwt import ExpiredSignatureError

from .client_analyzer import ClientAnalyzer
from .cookie import CookieService
from .errors import (
    RefreshSessionDoesNotExistError,
    RefreshSessionExpiredError
)
from ..jwt_ import (
    JWTBlacklistService,
    JWTService
)
from ...api.dependencies.markers import AppSettingsMarker
from ...core.settings import AppSettings
from ...db.errors import EntityDoesNotExistError
from ...db.models import (
    RefreshSession,
    User
)
from ...db.repos import RefreshSessionsRepo
from ...schemas.auth import (
    AuthResult,
    CredentialsInResponse
)
from ...utils.datetime_ import compute_expire


__all__ = ['Authenticator']

logger = logging.getLogger(__name__)


@dataclass
class Authenticator:
    jwt_service: JWTService = Depends()
    repo: RefreshSessionsRepo = Depends()
    cookie_service: CookieService = Depends()
    client_analyzer: ClientAnalyzer = Depends()
    settings: AppSettings = Depends(AppSettingsMarker)
    blacklist_service: JWTBlacklistService = Depends()

    async def authenticate(self, user: User) -> AuthResult:
        session = await self._create(user)
        self.cookie_service.set_refresh_token(session.refresh_token)
        return AuthResult(
            credentials=self._form_credentials(session),
            user=user
        )

    async def _create(self, user: User) -> RefreshSession:
        return await self.repo.create_one(
            user_id=user.id,
            ip_address=self.client_analyzer.ip_address,
            user_agent=self.client_analyzer.user_agent,
            expires_at=compute_expire(self.expire_in_seconds),
            access_token=self.jwt_service.generate(user)
        )

    @property
    def expire_in_seconds(self) -> int:
        return self.settings.refresh_token_expire_in_seconds

    def _form_credentials(
        self,
        session: RefreshSession
    ) -> CredentialsInResponse:
        return CredentialsInResponse(
            access_token=session.access_token,
            expires_in=self.settings.access_token_expire_in_seconds,
            refresh_token=session.refresh_token
        )

    async def deauthenticate(
        self,
        refresh_token: str
    ) -> None:
        session = await self.validate_refresh_session(refresh_token)
        await self.blacklist_access_token(session.access_token)
        self.cookie_service.delete_refresh_token()

    async def validate_refresh_session(
        self,
        refresh_token: str
    ) -> RefreshSession:
        session = await self._pull_refresh_session(refresh_token)
        if session.is_expired:
            raise RefreshSessionExpiredError
        return session

    async def _pull_refresh_session(
        self,
        refresh_token: str
    ) -> RefreshSession:
        try:
            session = await self.repo.delete_one_by_refresh_token(refresh_token)
        except EntityDoesNotExistError as error:
            raise RefreshSessionDoesNotExistError from error
        else:
            return session

    async def blacklist_access_token(self, token: str) -> None:
        with suppress(ExpiredSignatureError):
            claims = self.jwt_service.verify(token)
            await self.blacklist_service.blacklist(
                jti=claims.meta.jti,
                exp=claims.meta.exp
            )
