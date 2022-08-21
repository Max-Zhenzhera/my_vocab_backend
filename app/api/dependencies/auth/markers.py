from dataclasses import dataclass

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from .auth import patched_http_bearer


__all__ = [
    'CurrentUserMarker',
    'CurrentSuperuserMarker'
]


@dataclass
class BaseUserMarker:
    """
    Since dammy classes are used
    for user markers at dependency injection
    swagger loses authorization interface.

    So, we aren't forgetting to plug
    security dependency in markers.
    """

    _: HTTPAuthorizationCredentials = Depends(patched_http_bearer)


class CurrentUserMarker(BaseUserMarker):
    """ Dependency marker to get the current user. """


class CurrentSuperuserMarker(BaseUserMarker):
    """ Dependency marker to get the current superuser. """
