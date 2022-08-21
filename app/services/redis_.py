import logging
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    TypeAlias
)

from redis import asyncio as aioredis


if TYPE_CHECKING:
    RedisClient: TypeAlias = aioredis.Redis[bytes]
else:
    RedisClient: TypeAlias = aioredis.Redis

__all__ = [
    'RedisClient',
    'RedisState'
]

logger = logging.getLogger(__name__)


@dataclass
class RedisState:
    url: str

    def __post_init__(self) -> None:
        self.redis = aioredis.from_url(self.url)
        logger.info('Redis state has been initialized.')

    def __call__(self) -> RedisClient:
        return self.redis

    async def shutdown(self) -> None:
        await self.redis.close()
        logger.info('Redis state has been shutdown.')
