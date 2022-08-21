import logging
from uuid import UUID

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException
)
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)

from ..dependencies.query.verification import VerificationCodeQuery
from ...resources.strings.verification import ACTION_REQUIRES_VERIFICATION
from ...schemas.auth import AuthResult
from ...schemas.fastapi_ import HTTPExceptionSchema
from ...schemas.user import (
    UserInCreate,
    UserInLogin
)
from ...services.auth import (
    Authenticator,
    AuthService
)
from ...services.auth.cookie import REFRESH_TOKEN_COOKIE_KEY
from ...services.auth.errors import (
    LoginError,
    LogoutError,
    RefreshError,
    RefreshSessionDoesNotExistError,
    RefreshSessionExpiredError,
    RegistrationError
)
from ...services.mail import MailService
from ...services.verification import VerificationService
from ...utils.open_api.cookies import (
    SetRefreshTokenCookieAsOpenAPIHeader,
    UnsetRefreshTokenCookieAsOpenAPIHeader
)


__all__ = ['router']

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path='/register',
    name='auth:register',
    summary='Register a new user.',
    response_model=AuthResult,
    responses={
        HTTP_200_OK: {
            'model': AuthResult,
            'description': 'User has been successfully registered.',
            'headers': {
                'Set-Cookie': SetRefreshTokenCookieAsOpenAPIHeader
            }
        },
        HTTP_400_BAD_REQUEST: {
            'model': HTTPExceptionSchema,
            'description': RegistrationError.detail
        },
        HTTP_401_UNAUTHORIZED: {
            'model': HTTPExceptionSchema,
            'description': 'Action has not been verified.'
        }
    }
)
async def register(
    payload: UserInCreate,
    code: int = VerificationCodeQuery,
    verification_service: VerificationService = Depends(),
    authentication_service: AuthService = Depends(),
    mail_service: MailService = Depends()
) -> AuthResult:
    """
    **Requires verification.** See [/verification](#/Verification)

    `Mail: thank for registering.`
    """

    if not await verification_service.verify(payload.email, code):
        raise HTTPException(
            HTTP_401_UNAUTHORIZED,
            ACTION_REQUIRES_VERIFICATION
        )
    try:
        auth_result = await authentication_service.register(payload)
    except RegistrationError as error:
        raise HTTPException(
            HTTP_400_BAD_REQUEST,
            error.detail
        )
    else:
        await verification_service.delete(payload.email)
        mail_service.send_thank_for_registering(auth_result.user)
        return auth_result


@router.post(
    path='/login',
    name='auth:login',
    summary='Login the user.',
    response_model=AuthResult,
    responses={
        HTTP_200_OK: {
            'model': AuthResult,
            'description': 'User has been successfully logged in.',
            'headers': {
                'Set-Cookie': SetRefreshTokenCookieAsOpenAPIHeader
            }
        },
        HTTP_401_UNAUTHORIZED: {
            'model': HTTPExceptionSchema,
            'description': LoginError.detail
        }
    }
)
async def login(
    user_in_login: UserInLogin,
    auth_service: AuthService = Depends(),
) -> AuthResult:
    try:
        result = await auth_service.login(user_in_login)
    except LoginError as error:
        raise HTTPException(
            HTTP_401_UNAUTHORIZED,
            error.detail
        )
    else:
        return result


@router.get(
    path='/logout',
    name='auth:logout',
    summary='Logout the user.',
    responses={
        HTTP_200_OK: {
            'model': None,
            'description': 'User has been successfully logged out.',
            'headers': {
                'Set-Cookie': UnsetRefreshTokenCookieAsOpenAPIHeader
            }
        },
        HTTP_400_BAD_REQUEST: {
            'model': HTTPExceptionSchema,
            'description': (
                f'- {RefreshSessionExpiredError.detail}'
                f'\n- {RefreshSessionDoesNotExistError.detail}'
            )
        }
    }
)
async def logout(
    refresh_token: UUID = Cookie(
        ...,
        alias=REFRESH_TOKEN_COOKIE_KEY
    ),
    authenticator: Authenticator = Depends()
) -> None:
    try:
        await authenticator.deauthenticate(str(refresh_token))
    except LogoutError as error:
        raise HTTPException(
            HTTP_400_BAD_REQUEST,
            error.detail
        )


@router.get(
    path='/refresh',
    name='auth:refresh',
    summary='Refresh the user`s session.',
    response_model=AuthResult,
    responses={
        HTTP_200_OK: {
            'model': AuthResult,
            'description': 'The user`s session has been successfully refreshed.',
            'headers': {
                'Set-Cookie': SetRefreshTokenCookieAsOpenAPIHeader
            }
        },
        HTTP_401_UNAUTHORIZED: {
            'model': HTTPExceptionSchema,
            'description': (
                f'- {RefreshSessionExpiredError.detail}'
                f'\n- {RefreshSessionDoesNotExistError.detail}'
            )
        }
    }
)
async def refresh(
    refresh_token: UUID = Cookie(
        ...,
        alias=REFRESH_TOKEN_COOKIE_KEY
    ),
    auth_service: AuthService = Depends()
) -> AuthResult:
    try:
        result = await auth_service.refresh(str(refresh_token))
    except RefreshError as error:
        raise HTTPException(
            HTTP_401_UNAUTHORIZED,
            error.detail
        )
    else:
        return result
