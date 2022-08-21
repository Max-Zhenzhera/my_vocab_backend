import logging
from dataclasses import dataclass

from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

from .config import BACKENDS_CONFIG


__all__ = ['OAuthState']

logger = logging.getLogger(__name__)


@dataclass
class OAuthState:
    settings: dict[str, str]

    def __post_init__(self) -> None:
        self.oauth = OAuth(Config(environ=self.settings))
        self._register_backends()
        logger.info('OAuth state has been set.')

    def _register_backends(self) -> None:
        for name, config in BACKENDS_CONFIG.items():
            self.oauth.register(name, **config)

    def __call__(self) -> OAuth:
        return self.oauth
