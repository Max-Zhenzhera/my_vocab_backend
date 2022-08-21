from dataclasses import dataclass

from fastapi import (
    Depends,
    Response
)

from ...api.dependencies.markers import AppSettingsMarker
from ...core.settings import AppSettings


__all__ = [
    'REFRESH_TOKEN_COOKIE_KEY',
    'REFRESH_TOKEN_PATH',
    'CookieService'
]

REFRESH_TOKEN_COOKIE_KEY = 'refresh_token'
REFRESH_TOKEN_PATH = '/api/auth'


@dataclass
class CookieService:
    response: Response
    settings: AppSettings = Depends(AppSettingsMarker)

    @property
    def refresh_token_max_age(self) -> int:
        return self.settings.refresh_token_expire_in_seconds

    def set_refresh_token(self, refresh_token: str) -> None:
        self.response.set_cookie(
            key=REFRESH_TOKEN_COOKIE_KEY,
            value=refresh_token,
            max_age=self.refresh_token_max_age,
            path=REFRESH_TOKEN_PATH,
            httponly=True
        )

    def delete_refresh_token(self) -> None:
        self.response.delete_cookie(
            key=REFRESH_TOKEN_COOKIE_KEY,
            path=REFRESH_TOKEN_PATH,
        )
