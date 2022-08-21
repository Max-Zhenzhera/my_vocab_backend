"""
Route works with DB.

Cleanup:
    - user_1
"""

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.settings import AppSettings
from app.db.models import User
from app.db.repos import RefreshSessionsRepo
from app.services.auth.errors import LoginError
from tests.test_api.common.auth import (
    assert_auth_result_is_correct,
    assert_refresh_session_is_created
)
from tests.test_api.dtos import MetaUser


ROUTE_NAME = 'auth:login'


async def test_response_when_user_with_such_email_does_not_exist(
    app: FastAPI,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    response = await client.post(
        app.url_path_for(ROUTE_NAME),
        json=meta_user_1.in_login.dict()
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == LoginError.detail


async def test_response_when_password_is_incorrect(
    app: FastAPI,
    no_auth_client_1: AsyncClient,
    meta_user_1: MetaUser
):
    payload = meta_user_1.in_login.copy(
        update={'password': 'incorrectPassword'}
    )
    assert payload.password != meta_user_1.password

    response = await no_auth_client_1.post(
        app.url_path_for(ROUTE_NAME),
        json=payload.dict()
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == LoginError.detail


async def test_response_on_success(
    settings: AppSettings,
    app: FastAPI,
    meta_user_1: MetaUser,
    no_auth_client_1: AsyncClient
):
    response = await no_auth_client_1.post(
        app.url_path_for(ROUTE_NAME),
        json=meta_user_1.in_login.dict()
    )

    assert_auth_result_is_correct(
        settings=settings,
        meta_user=meta_user_1,
        response=response
    )


async def test_create_refresh_session_on_success(
    settings: AppSettings,
    app: FastAPI,
    db_session: AsyncSession,
    meta_user_1: MetaUser,
    user_1: User,
    no_auth_client_1: AsyncClient
):
    response = await no_auth_client_1.post(
        app.url_path_for(ROUTE_NAME),
        json=meta_user_1.in_login.dict()
    )

    await assert_refresh_session_is_created(
        settings=settings,
        repo=RefreshSessionsRepo(db_session),
        response=response
    )
