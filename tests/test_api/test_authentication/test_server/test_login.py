from dataclasses import replace as dataclasses_replace
from typing import (
    Any,
    ClassVar
)

import pytest
from httpx import AsyncClient
from starlette.datastructures import URLPath
from starlette.status import HTTP_401_UNAUTHORIZED

from app.schemas.entities.user import UserInLogin
from ..base import BaseTestAuthRouteCase
from ...base import BaseTestRoute
from ...dataclasses_ import MetaUser
from ...mixins.response_and_client import ResponseAndClient


pytestmark = pytest.mark.asyncio


class LoginRouteNameMixin:
    route_name: ClassVar[str] = 'auth:login'


class TestLoginRouteSingleCase(
    LoginRouteNameMixin,
    BaseTestAuthRouteCase
):
    @pytest.fixture(name='success_route_body')
    def fixture_success_route_body(
            self,
            meta_user_1: MetaUser
    ) -> dict[str, Any]:
        return meta_user_1.in_login.dict()

    @pytest.fixture(name='response_and_client_on_success')
    async def fixture_response_and_client_on_success(
            self,
            route_url: URLPath,
            success_route_body: dict[str, Any],
            unauthenticated_client_1: AsyncClient
    ) -> ResponseAndClient:
        return (
            await unauthenticated_client_1.post(
                url=route_url,
                json=success_route_body
            ),
            unauthenticated_client_1
        )


class TestCommonErrorsOfLoginRoute(
    LoginRouteNameMixin,
    BaseTestRoute
):
    @pytest.fixture(name='bad_route_body_with_nonexistent_user')
    def fixture_bad_route_body_with_nonexistent_user(self) -> dict[str, Any]:
        return UserInLogin(
            email='nonexistentuser@gmail.com',
            password='somePassword'
        ).dict()

    @pytest.fixture(name='bad_route_body_with_false_password')
    def fixture_bad_route_body_with_false_password(
            self,
            meta_user_1: MetaUser
    ) -> dict[str, Any]:
        return dataclasses_replace(
            meta_user_1,
            password=f'BreakPassword{meta_user_1.password}'
        ).in_login.dict()

    async def test_return_401_error_on_passing_credentials_of_nonexistent_user(
            self,
            route_url: URLPath,
            bad_route_body_with_nonexistent_user: dict[str, Any],
            client: AsyncClient
    ):
        """
        On login has been passed the credentials of the nonexistent user.

        Must return 401 Unauthorized.
        """

        unauthorized_response = await client.post(
            url=route_url,
            json=bad_route_body_with_nonexistent_user
        )

        assert unauthorized_response.status_code == HTTP_401_UNAUTHORIZED

    async def test_return_401_error_on_passing_false_password(
            self,
            route_url: URLPath,
            bad_route_body_with_false_password: dict[str, Any],
            unauthenticated_client_1: AsyncClient
    ):
        """
        On login has been passed the false password.

        Must return 401 Unauthorized.
        """

        unauthorized_response = await unauthenticated_client_1.post(
            url=route_url,
            json=bad_route_body_with_false_password
        )

        assert unauthorized_response.status_code == HTTP_401_UNAUTHORIZED
