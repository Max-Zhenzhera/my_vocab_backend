from dataclasses import dataclass


__all__ = ['OAuthUser']


@dataclass
class OAuthUser:
    id: str
    """ OAuth sub. """
    email: str
    """ Email of the connected OAuth user. """
    detail: str
    """ Nickname, Full name or at least email of the connected OAuth user. """
    is_email_taken: bool | None = None
    """ Flag can be set on callback for further handling. """
