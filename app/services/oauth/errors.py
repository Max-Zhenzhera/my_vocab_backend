"""
InternalOAuthError
    +-- OAuthConnectionDoesNotExistError
"""


class InternalOAuthError(Exception):
    """
    Name is redundant to not confuse with authlib error
    """


class OAuthConnectionDoesNotExistError(InternalOAuthError):
    """
    Raised on OAuth login process
    if the OAuth connection does not exist.
    """
