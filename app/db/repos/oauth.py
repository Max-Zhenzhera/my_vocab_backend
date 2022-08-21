from typing import ClassVar

from .base import BaseRepo
from ..enums import OAuthBackend
from ..models import OAuthConnection
from ...dtos.oauth import OAuthUser


__all__ = ['OAuthConnectionsRepo']


class OAuthConnectionsRepo(BaseRepo[OAuthConnection]):
    model: ClassVar = OAuthConnection

    async def link(
        self,
        oauth_user: OAuthUser,
        internal_user_id: int,
        backend: OAuthBackend
    ) -> OAuthConnection:
        return await self.create_one(
            oauth_id=oauth_user.id,
            backend=backend,
            email=oauth_user.email,
            detail=oauth_user.detail,
            user_id=internal_user_id
        )
