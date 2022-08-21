from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from app.db.enums import OAuthBackend
from app.db.errors import EntityDoesNotExistError
from app.db.repos import OAuthConnectionsRepo
from app.dtos.oauth import OAuthUser
from app.schemas.user import (
    UserInCreate,
    UserInOAuthCreate
)
from app.services.auth import (
    Authenticator,
    AuthService
)
from app.services.oauth import OAuthService
from app.services.oauth.errors import OAuthConnectionDoesNotExistError


@pytest.fixture
def auth_service() -> Mock:
    return Mock(
        AuthService,
        authenticator=Mock(Authenticator)
    )


@pytest.fixture
def repo() -> Mock:
    return Mock(OAuthConnectionsRepo)


@pytest.fixture
def service(
    auth_service: Mock,
    repo: Mock,
    set_ctx_backend: None
) -> OAuthService:
    return OAuthService(
        service=auth_service,
        repo=repo
    )


@pytest.fixture
def authenticator(
    service: OAuthService
) -> Authenticator:
    return service.authenticator


@pytest.fixture
def payload() -> UserInOAuthCreate:
    return UserInOAuthCreate(
        username='superUsername',
        password='userPassword'
    )


@pytest.fixture
def oauth_user() -> OAuthUser:
    return OAuthUser(
        id='12345',
        email='user@gmail.com',
        detail='Name Surname'
    )


async def test_register__use_server_register(
    auth_service: Mock,
    service: OAuthService,
    payload: UserInOAuthCreate,
    oauth_user: OAuthUser
):
    result = await service.register(oauth_user, payload)

    user_in_create: UserInCreate = auth_service.register.call_args.args[0]
    assert user_in_create.email == oauth_user.email
    assert user_in_create.password == payload.password
    auth_service.register.assert_called_once()
    assert result is auth_service.register.return_value


async def test_register__link_connection_to_internal_user(
    mocker: MockerFixture,
    backend: OAuthBackend,
    repo: Mock,
    auth_service: Mock,
    service: OAuthService,
    payload: UserInOAuthCreate,
    oauth_user: OAuthUser
):
    service_link = mocker.patch(
        'app.services.oauth.service.OAuthService.link'
    )

    await service.register(oauth_user, payload)

    internal_user = auth_service.register.return_value.user
    service_link.assert_called_once_with(oauth_user, internal_user.id)


async def test_login__raise_error_if_connection_does_not_exist(
    repo: Mock,
    service: OAuthService,
    oauth_user: OAuthUser
):
    repo.get_one_by_pk.side_effect = EntityDoesNotExistError

    with pytest.raises(OAuthConnectionDoesNotExistError):
        await service.login(oauth_user)


async def test_login__authenticate_user_from_db(
    repo: Mock,
    authenticator: Mock,
    service: OAuthService,
    oauth_user: OAuthUser
):
    result = await service.login(oauth_user)

    connection = repo.get_one_by_pk.return_value
    authenticator.authenticate.assert_called_once_with(connection.user)
    assert result is authenticator.authenticate.return_value


async def test_link__create_connection(
    backend: OAuthBackend,
    repo: Mock,
    service: OAuthService,
    oauth_user: OAuthUser
):
    internal_user_id = 12345

    result = await service.link(oauth_user, internal_user_id)

    kwargs = repo.link.call_args.kwargs
    assert kwargs['oauth_user'] == oauth_user
    assert kwargs['internal_user_id'] == internal_user_id
    assert kwargs['backend'] == backend
    assert result is repo.link.return_value
