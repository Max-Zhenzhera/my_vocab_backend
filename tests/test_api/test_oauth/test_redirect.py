"""
Route does not work with data backends.
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from httpx import AsyncClient
from pytest_mock import MockerFixture
from starlette.status import HTTP_302_FOUND

from app.db.enums import OAuthBackend


ROUTE_NAME = 'oauth:redirect'


async def test_response(
    mocker: MockerFixture,
    app: FastAPI,
    client: AsyncClient
):
    redirect_location = 'https://google.com'
    authorize_redirect = mocker.patch(
        'authlib.integrations.starlette_client.apps.'
        'StarletteAppMixin.authorize_redirect'
    )
    authorize_redirect.return_value = RedirectResponse(
        url=redirect_location,
        status_code=HTTP_302_FOUND
    )

    response = await client.get(
        app.url_path_for(
            ROUTE_NAME,
            backend=OAuthBackend.GOOGLE.value
        )
    )

    assert response.status_code == HTTP_302_FOUND
    assert response.headers['location'] == redirect_location
