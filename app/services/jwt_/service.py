from dataclasses import (
    asdict,
    dataclass
)
from typing import (
    Any,
    TypeAlias
)
from uuid import uuid4

import jwt
from fastapi import Depends

from ...api.dependencies.markers import AppSettingsMarker
from ...core.settings import AppSettings
from ...db.models import User
from ...dtos.jwt_ import (
    JWTClaims,
    JWTMetaClaims,
    JWTUserClaims
)
from ...utils.casts import to_dataclass
from ...utils.datetime_ import compute_expire


__all__ = ['JWTService']

TokenClaims: TypeAlias = dict[str, Any]


@dataclass
class JWTService:
    settings: AppSettings = Depends(AppSettingsMarker)

    def _encode(self, claims: TokenClaims) -> str:
        return jwt.encode(
            claims,
            self.settings.jwt_secret,
            self.settings.jwt_algorithm
        )

    def _decode(self, token: str) -> TokenClaims:
        return jwt.decode(
            token,
            self.settings.jwt_secret,
            [self.settings.jwt_algorithm]
        )

    def generate(self, user: User) -> str:
        claims = self._form_claims(user)
        return self._encode(claims)

    def _form_claims(self, user: User) -> TokenClaims:
        meta_claims = self._form_meta_claims(user)
        user_claims = self._form_user_claims(user)
        return asdict(meta_claims) | asdict(user_claims)

    @staticmethod
    def _form_user_claims(user: User) -> JWTUserClaims:
        return to_dataclass(JWTUserClaims, user)

    def _form_meta_claims(self, user: User) -> JWTMetaClaims:
        return JWTMetaClaims(
            sub=str(user.id),
            exp=compute_expire(self.expire_in_seconds, as_int=True),
            jti=self.generate_jti()
        )

    @property
    def expire_in_seconds(self) -> int:
        return self.settings.access_token_expire_in_seconds

    @staticmethod
    def generate_jti() -> str:
        return uuid4().hex

    def verify(self, token: str) -> JWTClaims:
        claims = self._decode(token)
        return self._parse_claims(claims)

    @staticmethod
    def _parse_claims(claims: TokenClaims) -> JWTClaims:
        return JWTClaims(
            meta=to_dataclass(JWTMetaClaims, claims),
            user=to_dataclass(JWTUserClaims, claims)
        )
