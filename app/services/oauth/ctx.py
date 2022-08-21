from contextvars import ContextVar

from ...db.enums import OAuthBackend


__all__ = ['ctx_oauth_backend']


ctx_oauth_backend: ContextVar[OAuthBackend] = ContextVar('ctx_oauth_provider')
