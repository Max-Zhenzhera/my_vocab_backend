import pytest

from app.db.enums import OAuthBackend
from app.services.oauth.ctx import ctx_oauth_backend


@pytest.fixture
def backend() -> OAuthBackend:
    return OAuthBackend.GOOGLE


@pytest.fixture
def set_ctx_backend(backend: OAuthBackend) -> None:
    ctx_oauth_backend.set(backend)
