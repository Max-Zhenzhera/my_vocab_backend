from dataclasses import dataclass


__all__ = ['JWTMetaClaims']


@dataclass
class JWTMetaClaims:
    exp: int
    sub: str
    jti: str
