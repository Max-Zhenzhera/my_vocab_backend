"""
Route works with Redis and DB.

Cleanup:
    - cleanup_redis
    - user_1
"""

from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST
)

from app.core.settings import AppSettings
from app.db.errors import EntityDoesNotExistError
from app.db.models import User
from app.db.repos import RefreshSessionsRepo
from app.services.auth.cookie import REFRESH_TOKEN_COOKIE_KEY
from app.services.auth.errors import (
    RefreshSessionDoesNotExistError,
    RefreshSessionExpiredError
)
from app.services.jwt_ import (
    JWTBlacklistService,
    JWTService
)
from app.utils.datetime_ import compute_expire
from tests.test_api.dtos import MetaUser


ROUTE_NAME = 'auth:logout'


@pytest.fixture(autouse=True)
async def cleanup_redis(flush_redis_db_after_test: None) -> None:
    pass


async def test_response_when_refresh_session_does_not_exist(
    app: FastAPI,
    client: AsyncClient
):
    response = await client.get(
        app.url_path_for(ROUTE_NAME),
        cookies={REFRESH_TOKEN_COOKIE_KEY: uuid4().hex}
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == RefreshSessionDoesNotExistError.detail


async def test_response_when_refresh_session_expired(
    app: FastAPI,
    db_session: AsyncSession,
    jwt_service: JWTService,
    meta_user_1: MetaUser,
    user_1: User,
    no_auth_client_1: AsyncClient
):
    refresh_session = await RefreshSessionsRepo(db_session).create_one(
        user_id=user_1.id,
        ip_address='127.0.0.1',
        user_agent='httpx',
        expires_at=compute_expire(-100),
        access_token=jwt_service.generate(user_1)
    )
    await db_session.commit()

    response = await no_auth_client_1.get(
        app.url_path_for(ROUTE_NAME),
        cookies={REFRESH_TOKEN_COOKIE_KEY: refresh_session.refresh_token}
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == RefreshSessionExpiredError.detail


async def test_response_on_success(
    settings: AppSettings,
    app: FastAPI,
    db_session: AsyncSession,
    jwt_service: JWTService,
    meta_user_1: MetaUser,
    user_1: User,
    no_auth_client_1: AsyncClient
):
    refresh_session = await RefreshSessionsRepo(db_session).create_one(
        user_id=user_1.id,
        ip_address='127.0.0.1',
        user_agent='httpx',
        expires_at=compute_expire(settings.refresh_token_expire_in_seconds),
        access_token=jwt_service.generate(user_1)
    )
    await db_session.commit()

    response = await no_auth_client_1.get(
        app.url_path_for(ROUTE_NAME),
        cookies={REFRESH_TOKEN_COOKIE_KEY: refresh_session.refresh_token}
    )

    assert response.status_code == HTTP_200_OK
    assert response.json() is None


async def test_blacklist_access_token_on_success(
    settings: AppSettings,
    app: FastAPI,
    db_session: AsyncSession,
    jwt_service: JWTService,
    jwt_blacklist_service: JWTBlacklistService,
    meta_user_1: MetaUser,
    user_1: User,
    no_auth_client_1: AsyncClient
):
    access_token = jwt_service.generate(user_1)
    refresh_session = await RefreshSessionsRepo(db_session).create_one(
        user_id=user_1.id,
        ip_address='127.0.0.1',
        user_agent='httpx',
        expires_at=compute_expire(settings.refresh_token_expire_in_seconds),
        access_token=access_token
    )
    await db_session.commit()
    token_claims = jwt_service.verify(access_token)

    await no_auth_client_1.get(
        app.url_path_for(ROUTE_NAME),
        cookies={REFRESH_TOKEN_COOKIE_KEY: refresh_session.refresh_token}
    )

    jti = token_claims.meta.jti
    assert await jwt_blacklist_service.check_is_blacklisted(jti)


async def test_delete_refresh_session_on_success(
    settings: AppSettings,
    app: FastAPI,
    db_session: AsyncSession,
    jwt_service: JWTService,
    meta_user_1: MetaUser,
    user_1: User,
    no_auth_client_1: AsyncClient
):
    refresh_session = await RefreshSessionsRepo(db_session).create_one(
        user_id=user_1.id,
        ip_address='127.0.0.1',
        user_agent='httpx',
        expires_at=compute_expire(settings.refresh_token_expire_in_seconds),
        access_token=jwt_service.generate(user_1)
    )
    await db_session.commit()

    await no_auth_client_1.get(
        app.url_path_for(ROUTE_NAME),
        cookies={REFRESH_TOKEN_COOKIE_KEY: refresh_session.refresh_token}
    )

    with pytest.raises(EntityDoesNotExistError):
        await (
            RefreshSessionsRepo(db_session)
            .get_one_by_refresh_token(refresh_session.refresh_token)
        )
