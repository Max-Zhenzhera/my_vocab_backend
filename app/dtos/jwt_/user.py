from dataclasses import dataclass


__all__ = ['JWTUserClaims']


@dataclass
class JWTUserClaims:
    id: int
    email: str
    username: str
    is_superuser: bool
