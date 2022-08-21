from unittest.mock import Mock

import pytest
from fastapi import Response

from app.core.settings import AppSettings
from app.services.auth.cookie import (
    REFRESH_TOKEN_COOKIE_KEY,
    REFRESH_TOKEN_PATH,
    CookieService
)


@pytest.fixture
def settings() -> Mock:
    return Mock(
        AppSettings,
        refresh_token_expire_in_seconds=100
    )


@pytest.fixture
def response() -> Mock:
    return Mock(Response)


@pytest.fixture
def service(
    settings: Mock,
    response: Mock
) -> CookieService:
    return CookieService(
        response=response,
        settings=settings
    )


def test_set_refresh_token__perform_setting_cookie(
    settings: Mock,
    response: Mock,
    service: CookieService,
):
    token = 'refreshToken'

    service.set_refresh_token(token)

    response.set_cookie.assert_called_once_with(
        key=REFRESH_TOKEN_COOKIE_KEY,
        value=token,
        max_age=settings.refresh_token_expire_in_seconds,
        path=REFRESH_TOKEN_PATH,
        httponly=True
    )


def test_set_refresh_token__perform_deleting_cookie(
    response: Mock,
    service: CookieService,
):
    service.delete_refresh_token()

    response.delete_cookie.assert_called_once_with(
        key=REFRESH_TOKEN_COOKIE_KEY,
        path=REFRESH_TOKEN_PATH,
    )
