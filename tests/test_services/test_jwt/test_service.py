from unittest.mock import Mock

import pytest

from app.core.settings import AppSettings
from app.db.models import User
from app.services.jwt_ import JWTService


@pytest.fixture
def settings() -> Mock:
    return Mock(
        AppSettings,
        access_token_expire_in_seconds=100,
        jwt_secret='jwtSecret',
        jwt_algorithm='HS256'
    )


@pytest.fixture
def service(
    settings: Mock
) -> JWTService:
    return JWTService(settings)


def test_generate_and_verify_work_correctly(
    service: JWTService
):
    user = Mock(
        User,
        id=12345,
        email='user@gmail.com',
        username='userUsername',
        is_superuser=False
    )

    token = service.generate(user)
    claims = service.verify(token)

    assert claims.meta.sub == str(user.id)
    assert claims.user.id == user.id
    assert claims.user.email == user.email
    assert claims.user.is_superuser == user.is_superuser
