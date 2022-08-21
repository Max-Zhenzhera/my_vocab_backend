import time
from unittest.mock import (
    AsyncMock,
    Mock
)

import pytest
from redis import asyncio as aioredis

from app.core.settings import AppSettings
from app.services.jwt_ import JWTBlacklistService


@pytest.fixture
def redis() -> Mock:
    return Mock(
        aioredis.Redis,
        set=AsyncMock(),
        exists=AsyncMock()
    )


@pytest.fixture
def settings() -> AppSettings:
    return Mock(
        AppSettings,
        access_token_expire_in_seconds=100
    )


@pytest.fixture
def service(
    redis: Mock,
    settings: Mock
) -> JWTBlacklistService:
    return JWTBlacklistService(
        redis=redis,
        settings=settings
    )


async def test_blacklist__pass_if_expired(
    redis: Mock,
    service: JWTBlacklistService
):
    await service.blacklist('jti', int(time.time()) - 5)

    redis.set.assert_not_called()


async def test_blacklist__create_redis_record(
    redis: Mock,
    settings: Mock,
    service: JWTBlacklistService
):
    jti, exp = 'jti', int(time.time()) + 50

    await service.blacklist(jti, exp)

    redis.set.assert_called_once_with(
        service.format_key(jti),
        0,
        settings.access_token_expire_in_seconds
    )


async def test_check_is_blacklisted__check_redis_record(
    redis: Mock,
    service: JWTBlacklistService
):
    jti = 'jti'

    await service.check_is_blacklisted(jti)

    redis.exists.assert_called_once_with(service.format_key(jti))
