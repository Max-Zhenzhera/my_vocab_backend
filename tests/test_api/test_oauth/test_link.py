"""
Route works with DB.

Cleanup:
    - user_1
"""

from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)

from app.core.settings import AppSettings
from app.db.enums import OAuthBackend
from app.db.repos import (
    OAuthConnectionsRepo,
    RefreshSessionsRepo
)
from app.resources.strings.oauth import (
    OAUTH_LINKING_WHEN_ACCOUNT_WITH_SUCH_EMAIL_EXISTS,
    OAUTH_USER_IS_NOT_IN_SESSION
)
from app.services.auth.errors import LoginError
from tests.test_api.common.auth import (
    assert_auth_result_is_correct,
    assert_oauth_connection_is_created,
    assert_refresh_session_is_created
)
from tests.test_api.dtos import MetaUser


ROUTE_NAME = 'oauth:link'


async def test_response_when_oauth_user_is_not_in_session(
    mocker: MockerFixture,
    app: FastAPI,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    get.return_value = None

    response = await client.post(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        ),
        json=meta_user_1.in_login.dict()
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == OAUTH_USER_IS_NOT_IN_SESSION


async def test_response_when_linking_to_other_account_but_email_is_taken(
    mocker: MockerFixture,
    app: FastAPI,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    oauth_user = meta_user_1.oauth
    oauth_user.is_email_taken = True
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    get.return_value = oauth_user
    payload = meta_user_1.in_login.copy(
        update={'email': f'not_a_{meta_user_1.email}'}
    )
    assert payload.email != meta_user_1.email

    response = await client.post(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        ),
        json=payload.dict()
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == (
        OAUTH_LINKING_WHEN_ACCOUNT_WITH_SUCH_EMAIL_EXISTS
    )


async def test_response_when_user_with_such_email_does_not_exist(
    mocker: MockerFixture,
    app: FastAPI,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    get.return_value = meta_user_1.oauth

    response = await client.post(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        ),
        json=meta_user_1.in_login.dict()
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == LoginError.detail


async def test_response_when_password_is_incorrect(
    mocker: MockerFixture,
    app: FastAPI,
    meta_user_1: MetaUser,
    client_1: AsyncClient
):
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    get.return_value = meta_user_1.oauth
    payload = meta_user_1.in_login.copy(
        update={'password': 'incorrectPassword'}
    )
    assert payload.password != meta_user_1.password

    response = await client_1.post(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        ),
        json=payload.dict()
    )

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == LoginError.detail


async def test_response_on_success(
    mocker: MockerFixture,
    settings: AppSettings,
    app: FastAPI,
    meta_user_1: MetaUser,
    client_1: AsyncClient
):
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    get.return_value = meta_user_1.oauth

    response = await client_1.post(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        ),
        json=meta_user_1.in_login.dict()
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
    client_1: AsyncClient
):
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    get.return_value = meta_user_1.oauth

    response = await client_1.post(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        ),
        json=meta_user_1.in_login.dict()
    )

    await assert_refresh_session_is_created(
        settings=settings,
        repo=RefreshSessionsRepo(db_session),
        response=response
    )


async def test_create_oauth_connection_on_success(
    mocker: MockerFixture,
    app: FastAPI,
    db_session: AsyncSession,
    meta_user_1: MetaUser,
    client_1: AsyncClient
):
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    get.return_value = meta_user_1.oauth
    backend = OAuthBackend.GOOGLE

    response = await client_1.post(
        app.url_path_for(
            ROUTE_NAME,
            backend=backend.value
        ),
        json=meta_user_1.in_login.dict()
    )

    await assert_oauth_connection_is_created(
        backend=backend,
        meta_user=meta_user_1,
        repo=OAuthConnectionsRepo(db_session),
        response=response
    )


async def test_delete_oauth_user_from_session_on_success(
    mocker: MockerFixture,
    app: FastAPI,
    meta_user_1: MetaUser,
    client_1: AsyncClient,
):
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    get.return_value = meta_user_1.oauth
    delete = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.delete'
    )

    await client_1.post(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        ),
        json=meta_user_1.in_login.dict()
    )

    delete.assert_called_once_with()
