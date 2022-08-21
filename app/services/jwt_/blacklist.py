import time
from dataclasses import dataclass
from typing import ClassVar

from fastapi import Depends

from ...api.dependencies.markers import (
    AppSettingsMarker,
    RedisMarker
)
from ...core.settings import AppSettings
from ...services.redis_ import RedisClient


__all__ = ['JWTBlacklistService']


@dataclass
class JWTBlacklistService:
    key_pattern: ClassVar[str] = 'blacklist:{jti}'
    redis: RedisClient = Depends(RedisMarker)
    settings: AppSettings = Depends(AppSettingsMarker)

    @staticmethod
    def format_key(jti: str) -> str:
        return JWTBlacklistService.key_pattern.format(jti=jti)

    @property
    def ex(self) -> int:
        return self.settings.access_token_expire_in_seconds

    async def blacklist(self, jti: str, exp: int) -> None:
        if exp < time.time():
            return
        await self.redis.set(self.format_key(jti), 0, self.ex)

    async def check_is_blacklisted(self, jti: str) -> bool:
        return bool(await self.redis.exists(self.format_key(jti)))
