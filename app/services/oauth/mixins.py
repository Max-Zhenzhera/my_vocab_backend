from .ctx import ctx_oauth_backend
from ...db.enums import OAuthBackend


__all__ = ['CtxOAuthBackendMixin']


class CtxOAuthBackendMixin:
    @property
    def backend(self) -> OAuthBackend:
        return ctx_oauth_backend.get()
