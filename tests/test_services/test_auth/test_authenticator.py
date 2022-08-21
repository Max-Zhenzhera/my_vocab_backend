from unittest.mock import Mock

import pytest
from jwt import ExpiredSignatureError
from pytest_mock import MockerFixture

from app.core.settings import AppSettings
from app.db.errors import EntityDoesNotExistError
from app.db.models import (
    RefreshSession,
    User
)
from app.db.repos import RefreshSessionsRepo
from app.services.auth import Authenticator
from app.services.auth.client_analyzer import ClientAnalyzer
from app.services.auth.cookie import CookieService
from app.services.auth.errors import (
    RefreshSessionDoesNotExistError,
    RefreshSessionExpiredError
)
from app.services.jwt_ import (
    JWTBlacklistService,
    JWTService
)


@pytest.fixture
def jwt_service() -> Mock:
    return Mock(JWTService)


@pytest.fixture
def repo() -> Mock:
    return Mock(RefreshSessionsRepo)


@pytest.fixture
def cookie_service() -> Mock:
    return Mock(CookieService)


@pytest.fixture
def client_analyzer() -> Mock:
    return Mock(ClientAnalyzer)


@pytest.fixture
def settings() -> Mock:
    return Mock(
        AppSettings,
        refresh_token_expire_in_seconds=200,
        access_token_expire_in_seconds=100,
    )


@pytest.fixture
def blacklist_service() -> Mock:
    return Mock(JWTBlacklistService)


@pytest.fixture
def authenticator(
    jwt_service: Mock,
    repo: Mock,
    cookie_service: Mock,
    client_analyzer: Mock,
    settings: Mock,
    blacklist_service: Mock
) -> Authenticator:
    return Authenticator(
        jwt_service=jwt_service,
        repo=repo,
        cookie_service=cookie_service,
        client_analyzer=client_analyzer,
        settings=settings,
        blacklist_service=blacklist_service
    )


@pytest.fixture
def user() -> Mock:
    return Mock(
        User,
        id=12345,
        username='superUsername',
        email='user@gmail.com',
        is_active=True,
        is_superuser=False
    )


@pytest.fixture
def refresh_session() -> Mock:
    return Mock(
        RefreshSession,
        access_token='accessToken',
        refresh_token='refreshToken',
        is_expired=False
    )


async def test_authenticate__create_session(
    jwt_service: Mock,
    repo: Mock,
    authenticator: Authenticator,
    user: Mock,
    refresh_session: Mock
):
    repo.create_one.return_value = refresh_session

    await authenticator.authenticate(user)

    repo.create_one.assert_called_once()
    kwargs = repo.create_one.call_args.kwargs
    assert kwargs['user_id'] == user.id
    jwt_service.generate.assert_called_once_with(user)
    assert kwargs['access_token'] == jwt_service.generate.return_value


async def test_authenticate__set_token_cookie(
    repo: Mock,
    cookie_service: Mock,
    authenticator: Authenticator,
    user: Mock,
    refresh_session: Mock
):
    repo.create_one.return_value = refresh_session

    await authenticator.authenticate(user)

    cookie_service.set_refresh_token.assert_called_once_with(
        refresh_session.refresh_token
    )


async def test_deauthenticate__validate_session(
    mocker: MockerFixture,
    repo: Mock,
    authenticator: Authenticator
):
    validate_refresh_session = mocker.patch(
        'app.services.auth.authenticator.Authenticator.validate_refresh_session'
    )
    token = 'refreshToken'

    await authenticator.deauthenticate(token)

    validate_refresh_session.assert_called_once_with(token)


async def test_deauthenticate__blacklist_access_token(
    mocker: MockerFixture,
    jwt_service: Mock,
    repo: Mock,
    blacklist_service: Mock,
    authenticator: Authenticator,
    refresh_session: Mock
):
    blacklist_access_token = mocker.patch(
        'app.services.auth.authenticator.Authenticator.blacklist_access_token'
    )
    repo.delete_one_by_refresh_token.return_value = refresh_session

    await authenticator.deauthenticate(refresh_session.refresh_token)

    blacklist_access_token.assert_called_once_with(refresh_session.access_token)


async def test_deauthenticate__delete_token_cookie(
    repo: Mock,
    cookie_service: Mock,
    authenticator: Authenticator,
    refresh_session: Mock
):
    repo.delete_one_by_refresh_token.return_value = refresh_session

    await authenticator.deauthenticate('refreshToken')

    cookie_service.delete_refresh_token.assert_called_once_with()


async def test_validate_refresh_session__delete_session(
    repo: Mock,
    authenticator: Authenticator,
    refresh_session: Mock
):
    repo.delete_one_by_refresh_token.return_value = refresh_session
    token = refresh_session.refresh_token

    await authenticator.validate_refresh_session(token)

    repo.delete_one_by_refresh_token.assert_called_once_with(token)


async def test_validate_refresh_session__raise_error_if_session_does_not_exist(
    repo: Mock,
    authenticator: Authenticator
):
    repo.delete_one_by_refresh_token.side_effect = EntityDoesNotExistError

    with pytest.raises(RefreshSessionDoesNotExistError):
        await authenticator.validate_refresh_session('refreshToken')


async def test_validate_refresh_session__raise_error_if_session_expired(
    repo: Mock,
    authenticator: Authenticator,
    refresh_session: Mock
):
    refresh_session.is_expired = True

    with pytest.raises(RefreshSessionExpiredError):
        await authenticator.validate_refresh_session('refreshToken')


async def test_blacklist_access_token__pass_if_token_expired(
    jwt_service: Mock,
    blacklist_service: Mock,
    authenticator: Authenticator
):
    jwt_service.verify.side_effect = ExpiredSignatureError

    await authenticator.blacklist_access_token('accessToken')

    blacklist_service.blacklist.assert_not_called()


async def test_blacklist_access_token__blacklist_token(
    jwt_service: Mock,
    blacklist_service: Mock,
    authenticator: Authenticator
):
    await authenticator.blacklist_access_token('accessToken')

    meta_claims = jwt_service.verify.return_value.meta
    blacklist_service.blacklist.assert_called_once_with(
        jti=meta_claims.jti,
        exp=meta_claims.exp
    )
