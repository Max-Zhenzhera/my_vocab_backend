from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from app.db.repos import UsersRepo
from app.services.auth import (
    Authenticator,
    AuthService,
    UserService
)


@pytest.fixture
def user_service() -> Mock:
    return Mock(
        UserService,
        repo=Mock(UsersRepo)
    )


@pytest.fixture
def authenticator() -> Mock:
    return Mock(Authenticator)


@pytest.fixture
def service(
    user_service: Mock,
    authenticator: Mock
) -> AuthService:
    return AuthService(
        user_service=user_service,
        authenticator=authenticator
    )


async def test_register__create_user(
    user_service: Mock,
    service: AuthService
):
    payload = Mock(BaseModel)

    await service.register(payload)

    user_service.create.assert_called_once_with(payload)


async def test_register__authenticate_user_from_db(
    user_service: Mock,
    authenticator: Mock,
    service: AuthService
):
    result = await service.register(Mock(BaseModel))

    authenticator.authenticate.assert_called_once_with(
        user_service.create.return_value
    )
    assert result is authenticator.authenticate.return_value


async def test_login__verify_user(
    user_service: Mock,
    service: AuthService
):
    payload = Mock(BaseModel)

    await service.login(payload)

    user_service.verify.assert_called_once_with(payload)


async def test_login__authenticate_user_from_db(
    user_service: Mock,
    authenticator: Mock,
    service: AuthService
):
    result = await service.login(Mock(BaseModel))

    authenticator.authenticate.assert_called_once_with(
        user_service.verify.return_value
    )
    assert result is authenticator.authenticate.return_value


async def test_refresh__validate_session(
    authenticator: Mock,
    service: AuthService
):
    token = 'refreshToken'

    await service.refresh(token)

    authenticator.validate_refresh_session.assert_called_once_with(token)


async def test_refresh__blacklist_access_token(
    authenticator: Mock,
    service: AuthService
):
    await service.refresh('refreshToken')

    refresh_session = authenticator.validate_refresh_session.return_value
    authenticator.blacklist_access_token.assert_called_once_with(
        refresh_session.access_token
    )


async def test_refresh__authenticate_user_from_db(
    user_service: Mock,
    authenticator: Mock,
    service: AuthService
):
    result = await service.refresh(Mock(BaseModel))

    authenticator.authenticate.assert_called_once_with(
        user_service.repo.get_one_by_pk.return_value
    )
    assert result is authenticator.authenticate.return_value
