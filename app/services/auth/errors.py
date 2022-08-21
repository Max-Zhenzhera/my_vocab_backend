"""
AuthError
    +-- LoginError
        +-- UserWithSuchEmailDoesNotExistError
        +-- IncorrectPasswordError
    +-- RegistrationError
        +-- EmailIsAlreadyTakenError
        +-- UsernameDiscriminatorsOutOfRange
    +-- RefreshError
        +-- RefreshSessionDoesNotExistError
        +-- RefreshSessionExpiredError
    +-- LogoutError
        +-- RefreshSessionDoesNotExistError
        +-- RefreshSessionExpiredError
"""


class AuthError(Exception):
    """ Common authentication exception. """
    detail = 'Authentication error.'


class LoginError(AuthError):
    """ Common login exception. """
    detail = 'Login failed. Credentials are invalid.'


class UserWithSuchEmailDoesNotExistError(LoginError):
    """
    Raised on login process
    if the searched user with the given email has not been found.
    """


class IncorrectPasswordError(LoginError):
    """
    Raised on login process
    if the given password has not been verified.
    """


class RegistrationError(AuthError):
    """ Common registration exception. """
    detail = 'Registration failed. Data is invalid.'


class EmailIsAlreadyTakenError(RegistrationError):
    """
    Raised on the registration process
    if the email is already used by the other user.
    """

    detail = 'Email is already taken.'


class UsernameIsAlreadyTakenError(RegistrationError):
    """
    Raised on the registration process
    if the username is already used by the other user.
    """

    detail = 'Username is already taken.'


class RefreshError(AuthError):
    """ Common refresh exception. """

    detail = 'Refresh error.'


class LogoutError(AuthError):
    """ Common logout exception. """

    detail = 'Refresh error.'


class RefreshSessionDoesNotExistError(LogoutError, RefreshError):
    """
    Raised on refresh/logout (validate) process
    if the refresh session with the given refresh token does not exist.
    """

    detail = 'Refresh session with such refresh token does not exist.'


class RefreshSessionExpiredError(LogoutError, RefreshError):
    """
    Raised on refresh/logout (validate) process
    if the refresh session has expired.
    """

    detail = 'Refresh session has expired.'
