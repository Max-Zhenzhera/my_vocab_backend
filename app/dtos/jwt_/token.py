from dataclasses import dataclass

from .meta import JWTMetaClaims
from .user import JWTUserClaims


__all__ = ['JWTClaims']


@dataclass
class JWTClaims:
    meta: JWTMetaClaims
    user: JWTUserClaims
