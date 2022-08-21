from fastapi import (
    Depends,
    HTTPException,
    Security
)
from fastapi.security import HTTPAuthorizationCredentials
from jwt import (
    ExpiredSignatureError,
    PyJWTError
)
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN
)

from .security import PatchedHTTPBearer
from ....dtos.jwt_ import JWTUserClaims
from ....resources.strings.auth import (
    ACCESS_TOKEN_EXPIRED,
    ACCESS_TOKEN_IS_IN_BLACKLIST,
    ACCESS_TOKEN_IS_INVALID,
    CURRENT_USER_IS_NOT_SUPERUSER
)
from ....services.jwt_ import (
    JWTBlacklistService,
    JWTService
)


__all__ = [
    'patched_http_bearer',
    'get_current_user',
    'get_current_superuser'
]

patched_http_bearer = PatchedHTTPBearer()


def _get_access_token(
    credentials: HTTPAuthorizationCredentials = Security(patched_http_bearer)
) -> str:
    return credentials.credentials


async def get_current_user(
    jwt_service: JWTService = Depends(),
    blacklist_service: JWTBlacklistService = Depends(),
    access_token: str = Depends(_get_access_token)
) -> JWTUserClaims:
    try:
        claims = jwt_service.verify(access_token)
    except ExpiredSignatureError:
        raise HTTPException(
            HTTP_401_UNAUTHORIZED,
            ACCESS_TOKEN_EXPIRED
        )
    except PyJWTError:
        raise HTTPException(
            HTTP_401_UNAUTHORIZED,
            ACCESS_TOKEN_IS_INVALID
        )
    else:
        if await blacklist_service.check_is_blacklisted(claims.meta.jti):
            raise HTTPException(
                HTTP_401_UNAUTHORIZED,
                ACCESS_TOKEN_IS_IN_BLACKLIST
            )
        return claims.user


def get_current_superuser(
    user: JWTUserClaims = Depends(get_current_user)
) -> JWTUserClaims:
    if not user.is_superuser:
        raise HTTPException(
            HTTP_403_FORBIDDEN,
            CURRENT_USER_IS_NOT_SUPERUSER
        )
    return user
