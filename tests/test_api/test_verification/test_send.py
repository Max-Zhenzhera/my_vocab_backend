"""
Route works with Redis.

Cleanup:
    - cleanup_redis
"""

import pytest
from fastapi import FastAPI
from fastapi_mail import FastMail
from httpx import AsyncClient
from pytest_mock import MockerFixture
from starlette.status import HTTP_200_OK

from app.db.enums import VerificationAction
from app.resources.mail.subjects import SUBJECT_FOR_VERIFICATION
from app.resources.mail.verification import (
    ACTION_TO_MESSAGE,
    DEFAULT_ACTION_MESSAGE
)
from app.schemas.verification import VerificationInCreate
from app.services.redis_ import RedisClient
from app.services.verification import VerificationService
from tests.utils.mail import check_mail_body_contains


ROUTE_NAME = 'verification:send'


@pytest.fixture(autouse=True)
async def cleanup_redis(flush_redis_db_after_test: None) -> None:
    pass


async def test_response(
    app: FastAPI,
    client: AsyncClient
):
    payload = VerificationInCreate(
        email='user@gmail.com',
        action=VerificationAction.REGISTRATION
    )

    response = await client.post(
        app.url_path_for(ROUTE_NAME),
        json=payload.dict()
    )

    assert response.status_code == HTTP_200_OK
    assert response.json() is None


async def test_create_verification_in_db_if_does_not_exist(
    app: FastAPI,
    redis: RedisClient,
    client: AsyncClient
):
    payload = VerificationInCreate(
        email='user@gmail.com',
        action=VerificationAction.REGISTRATION
    )

    await client.post(
        app.url_path_for(ROUTE_NAME),
        json=payload.dict()
    )

    code = await redis.get(VerificationService.format_key(payload.email))
    assert code is not None


async def test_use_verification_from_db_if_exists(
    mocker: MockerFixture,
    app: FastAPI,
    redis: RedisClient,
    client: AsyncClient
):
    send_verification = mocker.patch(
        'app.services.mail.service.MailService.send_verification'
    )
    payload = VerificationInCreate(
        email='user@gmail.com',
        action=VerificationAction.REGISTRATION
    )
    code = VerificationService.generate_code()
    await redis.set(
        VerificationService.format_key(payload.email),
        code
    )

    await client.post(
        app.url_path_for(ROUTE_NAME),
        json=payload.dict()
    )

    send_verification.assert_called_once_with(
        payload,
        VerificationService.format_code(code)
    )


async def test_send_verification_mail(
    app: FastAPI,
    redis: RedisClient,
    mail_sender: FastMail,
    client: AsyncClient
):
    payload = VerificationInCreate(
        email='user@gmal.com',
        action=VerificationAction.REGISTRATION
    )
    code = VerificationService.generate_code()
    await redis.set(
        VerificationService.format_key(payload.email),
        code
    )

    with mail_sender.record_messages() as outbox:
        await client.post(
            app.url_path_for(ROUTE_NAME),
            json=payload.dict()
        )

    mail = outbox[0]
    assert mail['subject'] == SUBJECT_FOR_VERIFICATION
    assert mail['to'] == payload.email
    assert check_mail_body_contains(
        mail,
        VerificationService.format_code(code)
    )
    assert check_mail_body_contains(
        mail,
        ACTION_TO_MESSAGE.get(payload.action, DEFAULT_ACTION_MESSAGE)
    )
