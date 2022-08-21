import logging

from authlib.integrations.starlette_client import (
    OAuth,
    OAuthError
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Request
)
from fastapi.responses import (
    JSONResponse,
    RedirectResponse
)
from starlette.status import (
    HTTP_200_OK,
    HTTP_300_MULTIPLE_CHOICES,
    HTTP_302_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)

from ..dependencies.markers import OAuthMarker
from ...db.enums import OAuthBackend
from ...db.repos import UsersRepo
from ...schemas.auth import AuthResult
from ...schemas.fastapi_ import HTTPExceptionSchema
from ...schemas.user import (
    UserInLogin,
    UserInOAuthCreate
)
from ...services.auth import AuthService
from ...services.auth.errors import (
    LoginError,
    RegistrationError
)
from ...services.mail import MailService
from ...services.oauth import (
    OAuthAuthorizer,
    OAuthRequestSession,
    OAuthService
)
from ...services.oauth.ctx import ctx_oauth_backend
from ...services.oauth.errors import OAuthConnectionDoesNotExistError
from app.resources.strings.oauth import (
    OAUTH_LINKING_WHEN_ACCOUNT_WITH_SUCH_EMAIL_EXISTS,
    OAUTH_USER_IS_NOT_IN_SESSION
)


__all__ = ['router']

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    path='/{backend}/redirect',
    name='oauth:redirect',
    summary='Redirect to the OAuth backend.',
    response_class=RedirectResponse,
    response_description='Redirected to OAuth backend.',
    status_code=HTTP_302_FOUND,
)
async def redirect(
    request: Request,
    backend: OAuthBackend = Path(...),
    oauth: OAuth = Depends(OAuthMarker)
) -> RedirectResponse:
    client = oauth.create_client(backend)
    return await client.authorize_redirect(  # type: ignore[no-any-return]
        request=request,
        redirect_uri=request.url_for('oauth:callback', backend=backend.value)
    )


@router.get(
    path='/{backend}/callback',
    name='oauth:callback',
    summary='Callback for the OAuth backend.',
    response_model=AuthResult,
    responses={
        HTTP_200_OK: {
            'model': AuthResult,
            'description': (
                'OAuth connection was successfully found, '
                'so user has been authenticated.'
            )
        },
        HTTP_300_MULTIPLE_CHOICES: {
            'model': None,
            'description': (
                'OAuth connection was not found. '
                'User has to choose how to continue:'
                '\n- Link to existed account '
                '(user has account with another email);'
                '\n- Create a new account.'
                '\n\nResult is empty.'
            )
        },
        HTTP_400_BAD_REQUEST: {
            'model': HTTPExceptionSchema,
            'description': 'Security issue on OAuth request processing.'
        },
        HTTP_401_UNAUTHORIZED: {
            'model': str,
            'description': (
                'Account with the email from OAuth already exists. '
                'To finish linking user has to pass a password.'
                '\n\nResult contains only the email string.'
            )
        }
    }
)
async def callback(
    backend: OAuthBackend = Path(...),
    users_repo: UsersRepo = Depends(),
    authorizer: OAuthAuthorizer = Depends(),
    oauth_service: OAuthService = Depends(),
    oauth_request_session: OAuthRequestSession = Depends()
) -> AuthResult | JSONResponse:
    ctx_oauth_backend.set(backend)
    try:
        oauth_user = await authorizer.get_oauth_user()
    except OAuthError as error:
        raise HTTPException(
            HTTP_400_BAD_REQUEST,
            error.error
        )
    else:
        try:
            auth_result = await oauth_service.login(oauth_user)
        except OAuthConnectionDoesNotExistError:
            oauth_user.is_email_taken = is_email_taken = (
                await users_repo.check_email_is_taken(oauth_user.email)
            )
            oauth_request_session.record(oauth_user)
            if is_email_taken:
                return JSONResponse(
                    oauth_user.email,
                    HTTP_401_UNAUTHORIZED
                )
            return JSONResponse(
                None,
                HTTP_300_MULTIPLE_CHOICES
            )
        else:
            return auth_result


@router.post(
    path='/{backend}/link',
    name='oauth:link',
    summary='Link OAuth to existed account.',
    response_model=AuthResult,
    responses={
        HTTP_200_OK: {
            'model': AuthResult,
            'description': (
                'OAuth connection has been linked '
                'to the internal user account.'
            )
        },
        HTTP_400_BAD_REQUEST: {
            'model': HTTPExceptionSchema,
            'description': (
                f'- {OAUTH_USER_IS_NOT_IN_SESSION}'
                f'\n- {OAUTH_LINKING_WHEN_ACCOUNT_WITH_SUCH_EMAIL_EXISTS}'
            )
        },
        HTTP_401_UNAUTHORIZED: {
            'model': HTTPExceptionSchema,
            'description': LoginError.detail
        }
    }
)
async def link(
    user_in_login: UserInLogin,
    backend: OAuthBackend = Path(...),
    auth_service: AuthService = Depends(),
    oauth_service: OAuthService = Depends(),
    oauth_request_session: OAuthRequestSession = Depends()
) -> AuthResult:
    ctx_oauth_backend.set(backend)
    if (oauth_user := oauth_request_session.get()) is None:
        raise HTTPException(
            HTTP_400_BAD_REQUEST,
            OAUTH_USER_IS_NOT_IN_SESSION
        )
    if (
        oauth_user.is_email_taken
        and user_in_login.email != oauth_user.email
    ):
        raise HTTPException(
            HTTP_400_BAD_REQUEST,
            OAUTH_LINKING_WHEN_ACCOUNT_WITH_SUCH_EMAIL_EXISTS
        )
    try:
        auth_result = await auth_service.login(user_in_login)
    except LoginError as error:
        raise HTTPException(
            HTTP_401_UNAUTHORIZED,
            error.detail
        )
    else:
        await oauth_service.link(oauth_user, auth_result.user.id)
        oauth_request_session.delete()
        return auth_result


@router.post(
    path='/{backend}/register',
    name='oauth:register',
    summary='Register a new account with OAuth.',
    response_model=AuthResult,
    responses={
        HTTP_200_OK: {
            'model': AuthResult,
            'description': (
                'OAuth user has been successfully registered '
                'a new account.'
            )
        },
        HTTP_400_BAD_REQUEST: {
            'model': HTTPExceptionSchema,
            'description': (
                f'- {OAUTH_USER_IS_NOT_IN_SESSION}'
                f'\n- {RegistrationError.detail}'
            )
        }
    }
)
async def register(
    user_in_oauth_create: UserInOAuthCreate,
    backend: OAuthBackend = Path(...),
    mail_service: MailService = Depends(),
    oauth_service: OAuthService = Depends(),
    oauth_request_session: OAuthRequestSession = Depends()
) -> AuthResult:
    ctx_oauth_backend.set(backend)
    if (oauth_user := oauth_request_session.get()) is None:
        raise HTTPException(
            HTTP_400_BAD_REQUEST,
            OAUTH_USER_IS_NOT_IN_SESSION
        )
    try:
        auth_result = await oauth_service.register(
            oauth_user=oauth_user,
            payload=user_in_oauth_create
        )
    except RegistrationError as error:
        raise HTTPException(
            HTTP_400_BAD_REQUEST,
            error.detail
        )
    else:
        oauth_request_session.delete()
        mail_service.send_thank_for_registering(auth_result.user)
        return auth_result
