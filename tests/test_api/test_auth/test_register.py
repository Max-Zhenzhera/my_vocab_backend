"""
Route works with Redis and DB.

Cleanup:
    - cleanup_redis
    - cleanup_db
"""

import pytest
from fastapi import FastAPI
from fastapi_mail import FastMail
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)

from app.core.settings import AppSettings
from app.db.repos import (
    RefreshSessionsRepo,
    UsersRepo
)
from app.services.auth.errors import (
    EmailIsAlreadyTakenError,
    UsernameIsAlreadyTakenError
)
from app.services.verification import VerificationService
from tests.test_api.common.auth import (
    assert_auth_result_is_correct,
    assert_refresh_session_is_created,
    assert_user_is_created
)
from tests.test_api.common.mail import assert_thank_mail_is_correct
from tests.test_api.dtos import MetaUser


ROUTE_NAME = 'auth:register'


@pytest.fixture(autouse=True)
async def cleanup_redis(flush_redis_db_after_test: None) -> None:
    pass


@pytest.fixture(autouse=True)
async def cleanup_db(delete_all_users_after_test: None) -> None:
    pass


async def test_response_when_verification_does_not_exist(
    app: FastAPI,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    response = await client.post(
        app.url_path_for(ROUTE_NAME),
        params={'code': VerificationService.generate_code()},
        json=meta_user_1.in_create.dict()
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED


async def test_response_when_verification_is_incorrect(
    app: FastAPI,
    verification_service: VerificationService,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    code = await verification_service.get(meta_user_1.email)
    incorrect_code = int(code) + 1
    assert incorrect_code != int(code)

    response = await client.post(
        app.url_path_for(ROUTE_NAME),
        params={'code': incorrect_code},
        json=meta_user_1.in_create.dict()
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED


async def test_response_when_email_is_taken(
    app: FastAPI,
    verification_service: VerificationService,
    meta_user_1: MetaUser,
    client_1: AsyncClient
):
    payload = meta_user_1.in_create.copy(
        update={'username': 'otherUsername'}
    )
    assert payload.username != meta_user_1.username
    code = await verification_service.get(payload.email)

    response = await client_1.post(
        app.url_path_for(ROUTE_NAME),
        params={'code': code},
        json=payload.dict()
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == EmailIsAlreadyTakenError.detail


async def test_response_when_username_is_taken(
    app: FastAPI,
    verification_service: VerificationService,
    meta_user_1: MetaUser,
    client_1: AsyncClient
):
    payload = meta_user_1.in_create.copy(
        update={'email': 'other@gmail.com'}
    )
    assert payload.email != meta_user_1.email
    code = await verification_service.get(payload.email)

    response = await client_1.post(
        app.url_path_for(ROUTE_NAME),
        params={'code': code},
        json=payload.dict()
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == UsernameIsAlreadyTakenError.detail


async def test_response_on_success(
    settings: AppSettings,
    app: FastAPI,
    verification_service: VerificationService,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    code = await verification_service.get(meta_user_1.email)

    response = await client.post(
        app.url_path_for(ROUTE_NAME),
        params={'code': code},
        json=meta_user_1.in_create.dict()
    )

    assert_auth_result_is_correct(
        settings=settings,
        meta_user=meta_user_1,
        response=response
    )


async def test_create_user_on_success(
    app: FastAPI,
    db_session: AsyncSession,
    verification_service: VerificationService,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    code = await verification_service.get(meta_user_1.email)

    response = await client.post(
        app.url_path_for(ROUTE_NAME),
        params={'code': code},
        json=meta_user_1.in_create.dict()
    )

    await assert_user_is_created(
        meta_user=meta_user_1,
        repo=UsersRepo(db_session),
        response=response
    )


async def test_create_refresh_session_on_success(
    settings: AppSettings,
    app: FastAPI,
    db_session: AsyncSession,
    verification_service: VerificationService,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    code = await verification_service.get(meta_user_1.email)

    response = await client.post(
        app.url_path_for(ROUTE_NAME),
        params={'code': code},
        json=meta_user_1.in_create.dict()
    )

    await assert_refresh_session_is_created(
        settings=settings,
        repo=RefreshSessionsRepo(db_session),
        response=response
    )


async def test_delete_verification_on_success(
    app: FastAPI,
    verification_service: VerificationService,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    code = await verification_service.get(meta_user_1.email)

    await client.post(
        app.url_path_for(ROUTE_NAME),
        params={'code': code},
        json=meta_user_1.in_create.dict()
    )

    key = verification_service.format_key(meta_user_1.email)
    db_code = await verification_service.raw_get(key)
    assert db_code is None


async def test_send_mail_on_success(
    app: FastAPI,
    mail_sender: FastMail,
    verification_service: VerificationService,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    code = await verification_service.get(meta_user_1.email)

    with mail_sender.record_messages() as outbox:
        await client.post(
            app.url_path_for(ROUTE_NAME),
            params={'code': code},
            json=meta_user_1.in_create.dict()
        )

    assert_thank_mail_is_correct(
        meta_user=meta_user_1,
        mail=outbox[0]
    )
