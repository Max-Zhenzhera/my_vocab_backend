from datetime import (
    datetime,
    timedelta
)
from typing import ClassVar

from .base import BaseRepo
from ..models import RefreshSession


__all__ = ['RefreshSessionsRepo']


class RefreshSessionsRepo(BaseRepo[RefreshSession]):
    model: ClassVar = RefreshSession

    async def get_one_by_refresh_token(
        self,
        refresh_token: str
    ) -> RefreshSession:
        return await self.get_one(
            [RefreshSession.refresh_token == refresh_token]
        )

    async def delete_one_by_refresh_token(
        self,
        refresh_token: str
    ) -> RefreshSession:
        return await self.delete_one(
            [RefreshSession.refresh_token == refresh_token]
        )

    async def expire(
        self,
        refresh_token: str,
        *,
        expires_at: datetime | None = None
    ) -> RefreshSession:
        expires_at = expires_at or datetime.utcnow() - timedelta(seconds=5)
        return await self.update_one(
            [RefreshSession.refresh_token == refresh_token],
            expires_at=expires_at
        )
