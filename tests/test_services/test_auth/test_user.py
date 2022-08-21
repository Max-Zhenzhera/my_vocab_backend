from unittest.mock import (
    AsyncMock,
    Mock
)

import pytest
from passlib.context import CryptContext

from app.db.errors import EntityDoesNotExistError
from app.db.repos import UsersRepo
from app.schemas.user import (
    UserInCreate,
    UserInLogin
)
from app.services.auth import UserService
from app.services.auth.errors import (
    EmailIsAlreadyTakenError,
    IncorrectPasswordError,
    UsernameIsAlreadyTakenError,
    UserWithSuchEmailDoesNotExistError
)


@pytest.fixture
def repo() -> Mock:
    return Mock(
        UsersRepo,
        check_email_is_taken=AsyncMock(return_value=False),
        check_username_is_taken=AsyncMock(return_value=False)
    )


@pytest.fixture
def pwd_context() -> Mock:
    return Mock(
        CryptContext,
        verify=Mock(return_value=True)
    )


@pytest.fixture
def service(
    repo: Mock,
    pwd_context: CryptContext
) -> UserService:
    return UserService(
        repo=repo,
        pwd_context=pwd_context
    )


@pytest.fixture
def payload_for_login() -> UserInLogin:
    return UserInLogin(
        email='user@gmail.com',
        password='userPassword'
    )


@pytest.fixture
def payload_for_create(
    payload_for_login: UserInLogin
) -> UserInCreate:
    return UserInCreate(
        **payload_for_login.dict(),
        username='superUsername'
    )


async def test_create__raise_error_if_email_is_taken(
    repo: Mock,
    service: UserService,
    payload_for_create: UserInCreate
):
    repo.check_email_is_taken.return_value = True

    with pytest.raises(EmailIsAlreadyTakenError):
        await service.create(payload_for_create)


async def test_create__raise_error_if_username_is_taken(
    repo: Mock,
    service: UserService,
    payload_for_create: UserInCreate
):
    repo.check_username_is_taken.return_value = True

    with pytest.raises(UsernameIsAlreadyTakenError):
        await service.create(payload_for_create)


async def test_create__create_user(
    repo: Mock,
    pwd_context: Mock,
    service: UserService,
    payload_for_create: UserInCreate
):
    result = await service.create(payload_for_create)

    pwd_context.hash.assert_called_once_with(payload_for_create.password)
    repo.create_one.assert_called_once()
    kwargs = repo.create_one.call_args.kwargs
    assert kwargs['hashed_password'] == pwd_context.hash.return_value
    assert result is repo.create_one.return_value


async def test_verify__raise_error_if_password_is_incorrect(
    pwd_context: Mock,
    service: UserService,
    payload_for_login: UserInLogin
):
    pwd_context.verify.return_value = False

    with pytest.raises(IncorrectPasswordError):
        await service.verify(payload_for_login)


async def test_verify__return_user_from_db(
    repo: Mock,
    service: UserService,
    payload_for_login: UserInLogin
):
    result = await service.verify(payload_for_login)

    assert result is repo.get_one_by_email.return_value


async def test_get_for_login__raise_error_if_user_does_not_exist(
    repo: Mock,
    service: UserService,
):
    repo.get_one_by_email.side_effect = EntityDoesNotExistError

    with pytest.raises(UserWithSuchEmailDoesNotExistError):
        await service.get_for_login('user@gmail.com')
