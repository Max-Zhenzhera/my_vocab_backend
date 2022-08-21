from dataclasses import (
    asdict,
    dataclass
)

from fastapi import Request

from .mixins import CtxOAuthBackendMixin
from ...db.enums import OAuthBackend
from ...dtos.oauth import OAuthUser


__all__ = ['OAuthRequestSession']


@dataclass
class OAuthRequestSession(CtxOAuthBackendMixin):
    request: Request

    @property
    def session_key(self) -> str:
        return self.format_key(self.backend)

    @staticmethod
    def format_key(backend: OAuthBackend) -> str:
        return f'oauth_{backend}'

    def record(self, oauth_user: OAuthUser) -> None:
        self.request.session[self.session_key] = asdict(oauth_user)

    def get(self) -> OAuthUser | None:
        data = self.request.session.get(self.session_key)
        return None if data is None else OAuthUser(**data)

    def delete(self) -> None:
        self.request.session.pop(self.session_key, None)
