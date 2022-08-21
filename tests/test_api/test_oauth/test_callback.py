"""
Route works with DB.

Cleanup:
    - user_1
"""

from authlib.integrations.starlette_client import OAuthError
from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import (
    HTTP_300_MULTIPLE_CHOICES,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)

from app.core.settings import AppSettings
from app.db.enums import OAuthBackend
from app.db.models import User
from app.db.repos import (
    OAuthConnectionsRepo,
    RefreshSessionsRepo
)
from tests.test_api.common.auth import (
    assert_auth_result_is_correct,
    assert_refresh_session_is_created
)
from tests.test_api.dtos import MetaUser


ROUTE_NAME = 'oauth:callback'


async def test_response_on_oauth_error(
    mocker: MockerFixture,
    app: FastAPI,
    client: AsyncClient
):
    get_oauth_user = mocker.patch(
        'app.services.oauth.authorizer.OAuthAuthorizer.get_oauth_user'
    )
    get_oauth_user.side_effect = OAuthError

    response = await client.get(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        )
    )

    assert response.status_code == HTTP_400_BAD_REQUEST


async def test_response_on_success(
    mocker: MockerFixture,
    settings: AppSettings,
    app: FastAPI,
    db_session: AsyncSession,
    meta_user_1: MetaUser,
    user_1: User,
    client_1: AsyncClient
):
    """ OAuth connection exists -> login succeeded. """
    backend = OAuthBackend.GOOGLE
    await OAuthConnectionsRepo(db_session).link(
        oauth_user=meta_user_1.oauth,
        internal_user_id=user_1.id,
        backend=backend
    )
    await db_session.commit()
    get_oauth_user = mocker.patch(
        'app.services.oauth.authorizer.OAuthAuthorizer.get_oauth_user'
    )
    get_oauth_user.return_value = meta_user_1.oauth

    response = await client_1.get(
        app.url_path_for(
            ROUTE_NAME,
            backend=backend.value
        )
    )

    assert_auth_result_is_correct(
        settings=settings,
        meta_user=meta_user_1,
        response=response
    )


async def test_create_refresh_session_on_success(
    mocker: MockerFixture,
    settings: AppSettings,
    app: FastAPI,
    db_session: AsyncSession,
    meta_user_1: MetaUser,
    user_1: User,
    client_1: AsyncClient
):
    """ OAuth connection exists -> login succeeded. """
    backend = OAuthBackend.GOOGLE
    await OAuthConnectionsRepo(db_session).link(
        oauth_user=meta_user_1.oauth,
        internal_user_id=user_1.id,
        backend=backend
    )
    await db_session.commit()
    get_oauth_user = mocker.patch(
        'app.services.oauth.authorizer.OAuthAuthorizer.get_oauth_user'
    )
    get_oauth_user.return_value = meta_user_1.oauth

    response = await client_1.get(
        app.url_path_for(
            ROUTE_NAME,
            backend=backend.value
        )
    )

    await assert_refresh_session_is_created(
        settings=settings,
        repo=RefreshSessionsRepo(db_session),
        response=response
    )


async def test_response_when_connection_does_not_exist_and_email_is_free(
    mocker: MockerFixture,
    settings: AppSettings,
    app: FastAPI,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    get_oauth_user = mocker.patch(
        'app.services.oauth.authorizer.OAuthAuthorizer.get_oauth_user'
    )
    get_oauth_user.return_value = meta_user_1.oauth

    response = await client.get(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        )
    )

    assert response.status_code == HTTP_300_MULTIPLE_CHOICES
    assert response.json() is None


async def test_response_when_connection_does_not_exist_but_email_is_taken(
    mocker: MockerFixture,
    settings: AppSettings,
    app: FastAPI,
    meta_user_1: MetaUser,
    client_1: AsyncClient
):
    get_oauth_user = mocker.patch(
        'app.services.oauth.authorizer.OAuthAuthorizer.get_oauth_user'
    )
    get_oauth_user.return_value = meta_user_1.oauth

    response = await client_1.get(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        )
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == meta_user_1.email


async def test_oauth_user_is_recorded_in_session_when_connection_does_not_exist(
    mocker: MockerFixture,
    app: FastAPI,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    get_oauth_user = mocker.patch(
        'app.services.oauth.authorizer.OAuthAuthorizer.get_oauth_user'
    )
    get_oauth_user.return_value = meta_user_1.oauth
    record = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.record'
    )

    await client.get(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        )
    )

    record.assert_called_once_with(get_oauth_user.return_value)
    assert isinstance(get_oauth_user.return_value.is_email_taken, bool)
