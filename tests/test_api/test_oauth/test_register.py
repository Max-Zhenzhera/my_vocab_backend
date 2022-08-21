"""
Route works with DB.

Cleanup:
    - cleanup_db
"""
import pytest
from fastapi import FastAPI
from fastapi_mail import FastMail
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from app.core.settings import AppSettings
from app.db.enums import OAuthBackend
from app.db.repos import (
    OAuthConnectionsRepo,
    RefreshSessionsRepo,
    UsersRepo
)
from app.resources.strings.oauth import OAUTH_USER_IS_NOT_IN_SESSION
from app.services.auth.errors import (
    EmailIsAlreadyTakenError,
    UsernameIsAlreadyTakenError
)
from tests.test_api.common.auth import (
    assert_auth_result_is_correct,
    assert_oauth_connection_is_created,
    assert_refresh_session_is_created,
    assert_user_is_created
)
from tests.test_api.common.mail import assert_thank_mail_is_correct
from tests.test_api.dtos import MetaUser


ROUTE_NAME = 'oauth:register'


@pytest.fixture(autouse=True)
async def cleanup_db(delete_all_users_after_test: None) -> None:
    pass


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
        json=meta_user_1.in_oauth_create.dict()
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == OAUTH_USER_IS_NOT_IN_SESSION


async def test_response_when_email_is_taken(
    mocker: MockerFixture,
    app: FastAPI,
    meta_user_1: MetaUser,
    client_1: AsyncClient
):
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    get.return_value = meta_user_1.oauth
    payload = meta_user_1.in_create.copy(
        update={'username': 'otherUsername'}
    )
    assert payload.username != meta_user_1.username

    response = await client_1.post(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        ),
        json=payload.dict()
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == EmailIsAlreadyTakenError.detail


async def test_response_when_username_is_taken(
    mocker: MockerFixture,
    app: FastAPI,
    meta_user_1: MetaUser,
    client_1: AsyncClient
):
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    oauth_user = meta_user_1.oauth
    oauth_user.email = f'not_a_{oauth_user.email}'
    assert oauth_user.email != meta_user_1.email
    get.return_value = oauth_user

    response = await client_1.post(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        ),
        json=meta_user_1.in_oauth_create.dict()
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == UsernameIsAlreadyTakenError.detail


async def test_response_on_success(
    mocker: MockerFixture,
    settings: AppSettings,
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
        json=meta_user_1.in_oauth_create.dict()
    )

    assert_auth_result_is_correct(
        settings=settings,
        meta_user=meta_user_1,
        response=response
    )


async def test_create_user_on_success(
    mocker: MockerFixture,
    app: FastAPI,
    db_session: AsyncSession,
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
        json=meta_user_1.in_oauth_create.dict()
    )

    await assert_user_is_created(
        meta_user=meta_user_1,
        repo=UsersRepo(db_session),
        response=response
    )


async def test_create_refresh_session_on_success(
    mocker: MockerFixture,
    settings: AppSettings,
    app: FastAPI,
    db_session: AsyncSession,
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
        json=meta_user_1.in_oauth_create.dict()
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
    client: AsyncClient
):
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    get.return_value = meta_user_1.oauth
    backend = OAuthBackend.GOOGLE

    response = await client.post(
        app.url_path_for(
            ROUTE_NAME,
            backend=backend.value
        ),
        json=meta_user_1.in_oauth_create.dict()
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
    client: AsyncClient,
):
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    get.return_value = meta_user_1.oauth
    delete = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.delete'
    )

    await client.post(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        ),
        json=meta_user_1.in_oauth_create.dict()
    )

    delete.assert_called_once_with()


async def test_send_mail_on_success(
    mocker: MockerFixture,
    app: FastAPI,
    mail_sender: FastMail,
    meta_user_1: MetaUser,
    client: AsyncClient
):
    get = mocker.patch(
        'app.services.oauth.session.OAuthRequestSession.get'
    )
    get.return_value = meta_user_1.oauth

    with mail_sender.record_messages() as outbox:
        await client.post(
            app.url_path_for(
                ROUTE_NAME,
                backend=OAuthBackend.GOOGLE.value
            ),
            json=meta_user_1.in_oauth_create.dict()
        )

    assert_thank_mail_is_correct(
        meta_user=meta_user_1,
        mail=outbox[0]
    )
