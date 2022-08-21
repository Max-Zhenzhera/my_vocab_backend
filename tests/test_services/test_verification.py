from unittest.mock import (
    AsyncMock,
    Mock
)

import pytest
from redis import asyncio as aioredis

from app.core.settings import AppSettings
from app.services.verification import VerificationService


@pytest.fixture
def redis() -> Mock:
    return Mock(
        aioredis.Redis,
        get=AsyncMock(),
        set=AsyncMock(),
        delete=AsyncMock()
    )


@pytest.fixture
def settings() -> Mock:
    return Mock(
        AppSettings,
        verification_code_expire_in_seconds=100
    )


@pytest.fixture
def service(
    settings: Mock,
    redis: Mock
) -> VerificationService:
    return VerificationService(
        redis=redis,
        settings=settings
    )


async def test_get__return_code_if_do_exist(
    redis: Mock,
    service: VerificationService
):
    email = 'user@gmail.com'
    redis.get.return_value = code = service.generate_code()

    result = await service.get(email)

    redis.get.assert_called_once_with(service.format_key(email))
    assert result == service.format_code(code)


async def test_get__create_code_if_does_not_exist(
    redis: Mock,
    settings: Mock,
    service: VerificationService
):
    redis.get.return_value = None
    email = 'user@gmail.com'

    result = await service.get(email)

    redis.set.assert_called_once_with(
        service.format_key(email),
        int(result),
        settings.verification_code_expire_in_seconds
    )


async def test_verify__return_false_if_code_does_not_exist(
    redis: Mock,
    service: VerificationService
):
    redis.get.return_value = None

    result = await service.verify(
        'user@gmail.com',
        service.generate_code()
    )

    assert not result


async def test_verify__return_false_if_code_is_incorrect(
    redis: Mock,
    service: VerificationService
):
    redis.get.return_value = code = service.generate_code()
    incorrect_code = code + 1
    assert incorrect_code != code

    result = await service.verify(
        'user@gmail.com',
        incorrect_code
    )

    assert not result


async def test_verify__return_true_on_success(
    redis: Mock,
    service: VerificationService
):
    redis.get.return_value = code = service.generate_code()

    result = await service.verify(
        'user@gmail.com',
        code
    )

    assert result


async def test_delete__delete_code(
    redis: Mock,
    service: VerificationService
):
    email = 'user@gmail.com'

    await service.delete(email)

    redis.delete.assert_called_once_with(service.format_key(email))
