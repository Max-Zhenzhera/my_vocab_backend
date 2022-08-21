from datetime import timedelta

from httpx import Response
from starlette.status import HTTP_200_OK

from app.core.settings import AppSettings
from app.db.enums import OAuthBackend
from app.db.models import OAuthConnection
from app.db.repos import (
    OAuthConnectionsRepo,
    RefreshSessionsRepo,
    UsersRepo
)
from tests.test_api.dtos import MetaUser


__all__ = [
    'assert_auth_result_is_correct',
    'assert_refresh_session_is_created',
    'assert_user_is_created',
    'assert_oauth_connection_is_created'
]


def assert_auth_result_is_correct(
    settings: AppSettings,
    meta_user: MetaUser,
    response: Response,
    *,
    status_code: int = HTTP_200_OK
) -> None:
    response_json = response.json()
    assert response.status_code == status_code
    assert all(
        claim in response_json['credentials']
        for claim in (
            'access_token',
            'expires_in',
            'token_type',
            'refresh_token'
        )
    )
    assert response_json['credentials']['expires_in'] == (
        settings.access_token_expire_in_seconds
    )
    assert response_json['user']['email'] == meta_user.email
    assert response_json['user']['username'] == meta_user.username
    assert (
        response.cookies['refresh_token']
        == response_json['credentials']['refresh_token']
    )


async def assert_refresh_session_is_created(
    settings: AppSettings,
    repo: RefreshSessionsRepo,
    response: Response,
    *,
    user_id: int | None = None

) -> None:
    response_json = response.json()
    access_token = response_json['credentials']['access_token']
    refresh_token = response_json['credentials']['refresh_token']
    session = await repo.get_one_by_refresh_token(refresh_token)
    assert session.user_id == (user_id or response_json['user']['id'])
    assert session.access_token == access_token
    expire_in_seconds = settings.refresh_token_expire_in_seconds
    expire_timedelta: timedelta = session.expires_at - session.created_at
    assert (
        int(expire_timedelta.total_seconds())
        in range(expire_in_seconds - 10, expire_in_seconds + 10)
    )


async def assert_user_is_created(
    meta_user: MetaUser,
    repo: UsersRepo,
    response: Response,
    *,
    is_superuser: bool = False
) -> None:
    user_id = int(response.json()['user']['id'])
    user = await repo.get_one_by_pk(user_id)
    assert user.email == meta_user.email
    assert user.username == meta_user.username
    assert user.is_superuser == is_superuser


async def assert_oauth_connection_is_created(
    backend: OAuthBackend,
    meta_user: MetaUser,
    repo: OAuthConnectionsRepo,
    response: Response
) -> None:
    connection = await repo.get_one_by_pk(
        [meta_user.oauth_id, backend],
        [OAuthConnection.user]
    )
    assert connection.user.id == response.json()['user']['id']
    assert connection.email == meta_user.email
