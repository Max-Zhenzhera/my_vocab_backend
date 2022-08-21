"""
Contains the patched `fastapi.security.http.HTTPBearer`.

Original `fastapi.security.http.HTTPBearer`
raises `HTTP_403_FORBIDDEN` on empty header and not a *bearer* token.

Patched to raise `HTTP_401_UNAUTHORIZED` on such errors.
"""

from fastapi import (
    HTTPException,
    Request
)
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_401_UNAUTHORIZED

from ....resources.strings.auth import (
    AUTHORIZATION_HEADER_IS_INVALID,
    TOKEN_IS_NOT_BEARER
)


__all__ = ['PatchedHTTPBearer']


class PatchedHTTPBearer(SecurityBase):
    def __init__(self) -> None:
        self.model = HTTPBearerModel()
        self.scheme_name = self.__class__.__name__

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        authorization: str = request.headers.get('Authorization')
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            raise HTTPException(HTTP_401_UNAUTHORIZED, AUTHORIZATION_HEADER_IS_INVALID)
        if scheme.lower() != 'bearer':
            raise HTTPException(HTTP_401_UNAUTHORIZED, TOKEN_IS_NOT_BEARER)
        return HTTPAuthorizationCredentials(
            scheme=scheme,
            credentials=credentials
        )
