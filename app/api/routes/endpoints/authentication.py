import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)

from ....schemas.authentication import AuthenticationResult
from ....schemas.user import (
    UserInCreate,
    UserInLogin,
    UserInResponse
)
from ....services.authentication import (
    AuthenticationService,
    CookieService
)
from ....services.authentication.errors import (
    AuthenticationError,
    RegistrationError
)
from ....services.mail import MailService


__all__ = ['router']


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/create', response_model=UserInResponse, name='auth:create')
async def create(
        user_in_create: UserInCreate,
        authentication_service: AuthenticationService = Depends()
):
    """
    Create a user by the given credentials.
    Route just creates a user in db. Mostly aims at the test fixtures or manual testing.

    Arguments
    ---------
        < UserInCreate > model

    Return
    ---------
        * Body
            < AuthenticationResult > model

    Raise
    ---------
        * 400 BAD REQUEST
            The given credentials are invalid or (most likely) already used before.
    """

    try:
        user = await authentication_service.create_user(user_in_create)
    except RegistrationError as error:
        raise HTTPException(HTTP_400_BAD_REQUEST, error.detail)
    else:
        return user


@router.post('/register', response_model=AuthenticationResult, name='auth:register')
async def register(
        user_in_create: UserInCreate,
        authentication_service: AuthenticationService = Depends(),
        cookie_service: CookieService = Depends(),
        mail_service: MailService = Depends()
):
    """
    Register a user by the given credentials.
    Route creates a user and logins him simultaneously.

    Arguments
    ---------
        < UserInCreate > model

    Return
    ---------
        * Body
            < AuthenticationResult > model
        * Cookies
            < refresh_token> httpOnly cookie

    Raise
    ---------
        * 400 BAD REQUEST
            The given credentials are invalid or (most likely) already used before.

    Other
    ---------
        * Email
            Send confirmation mail to indicated email.
    """

    try:
        authentication_result = await authentication_service.register(user_in_create)
    except RegistrationError as error:
        raise HTTPException(HTTP_400_BAD_REQUEST, error.detail)
    else:
        cookie_service.set_refresh_token(authentication_result.tokens.refresh_token)
        mail_service.send_confirmation_mail(authentication_result.user)
        return authentication_result


@router.post('/login', response_model=AuthenticationResult, name='auth:login')
async def login(
        user_in_login: UserInLogin,
        authentication_service: AuthenticationService = Depends(),
        cookie_service: CookieService = Depends()
):
    """
    Login a user by the given credentials.

    Arguments
    ---------
        < UserInLogin > model

    Return
    ---------
        * Body
            < AuthenticationResult > model
        * Cookies
            < refresh_token> httpOnly cookie

    Raise
    ---------
        * 401 UNAUTHORIZED
            The incorrect credentials.
    """

    try:
        authentication_result = await authentication_service.login(user_in_login)
    except AuthenticationError as error:
        raise HTTPException(HTTP_401_UNAUTHORIZED, error.detail)
    else:
        cookie_service.set_refresh_token(authentication_result.tokens.refresh_token)
        return authentication_result
