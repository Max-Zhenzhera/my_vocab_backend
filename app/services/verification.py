import secrets
from dataclasses import dataclass
from typing import ClassVar

from fastapi import Depends

from .redis_ import RedisClient
from ..api.dependencies.markers import (
    AppSettingsMarker,
    RedisMarker
)
from ..core.settings import AppSettings


__all__ = [
    'VERIFICATION_CODE_LENGTH',
    'VERIFICATION_CODES_RANGE',
    'VerificationService'
]

VERIFICATION_CODE_LENGTH = 6
VERIFICATION_CODES_RANGE = range(1, 10 ** VERIFICATION_CODE_LENGTH)


@dataclass
class VerificationService:
    key_pattern: ClassVar[str] = 'verification:{email}'
    redis: RedisClient = Depends(RedisMarker)
    settings: AppSettings = Depends(AppSettingsMarker)

    @staticmethod
    def generate_code() -> int:
        return secrets.choice(VERIFICATION_CODES_RANGE)

    @staticmethod
    def format_key(email: str) -> str:
        return VerificationService.key_pattern.format(email=email)

    @staticmethod
    def format_code(code: int) -> str:
        return str(code).zfill(VERIFICATION_CODE_LENGTH)

    @property
    def ex(self) -> int:
        return self.settings.verification_code_expire_in_seconds

    async def get(self, email: str) -> str:
        key = self.format_key(email)
        if (code := await self.raw_get(key)) is not None:
            return self.format_code(code)
        code = self.generate_code()
        await self.redis.set(key, code, self.ex)
        return self.format_code(code)

    async def verify(self, email: str, code: int) -> bool:
        db_code = await self.raw_get(self.format_key(email))
        if db_code is None or db_code != code:
            return False
        return True

    async def raw_get(self, key: str) -> int | None:
        code = await self.redis.get(key)
        return int(code) if code is not None else None

    async def delete(self, email: str) -> None:
        await self.redis.delete(self.format_key(email))
