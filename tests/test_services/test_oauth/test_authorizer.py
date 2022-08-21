from unittest.mock import Mock

import pytest
from authlib.integrations.starlette_client import (
    OAuth,
    StarletteOAuth2App
)
from fastapi import Request
from pytest_mock import MockerFixture

from app.services.oauth import OAuthAuthorizer


@pytest.fixture
def request_() -> Mock:
    return Mock(Request)


@pytest.fixture
def oauth() -> Mock:
    return Mock(OAuth)


@pytest.fixture
def authorizer(
    set_ctx_backend: None,
    request_: Mock,
    oauth: Mock
) -> OAuthAuthorizer:
    return OAuthAuthorizer(
        request=request_,
        oauth=oauth
    )


@pytest.fixture
def client(
    mocker: MockerFixture,
) -> Mock:
    return mocker.patch(
        'app.services.oauth.authorizer.OAuthAuthorizer.client',
        spec=StarletteOAuth2App
    )


async def test_get_oauth_user__cast_userinfo_to_specific_backend(
    mocker: MockerFixture,
    authorizer: OAuthAuthorizer
):
    userinfo_caster = Mock()
    mocker.patch(
        'app.services.oauth.authorizer.OAuthAuthorizer.get_userinfo_caster',
        return_value=userinfo_caster
    )
    get_userinfo = mocker.patch(
        'app.services.oauth.authorizer.OAuthAuthorizer.get_userinfo'
    )

    await authorizer.get_oauth_user()

    userinfo_caster.assert_called_once_with(get_userinfo.return_value)


async def test_get_userinfo__return_userinfo_from_token_if_present(
    request_: Mock,
    authorizer: OAuthAuthorizer,
    client: Mock
):
    userinfo = {'data': True}
    token = {'userinfo': userinfo}
    client.authorize_access_token.return_value = token

    result = await authorizer.get_userinfo()

    client.authorize_access_token.assert_called_once_with(request_)
    assert result is userinfo


async def test_get_userinfo__return_userinfo_from_extra_request_if_token_is_empty(
    request_: Mock,
    authorizer: OAuthAuthorizer,
    client: Mock
):
    token = {'access_token': 'accessToken'}
    client.authorize_access_token.return_value = token

    result = await authorizer.get_userinfo()

    client.authorize_access_token.assert_called_once_with(request_)
    client.userinfo.assert_called_once_with(token=token)
    assert result is client.userinfo.return_value
