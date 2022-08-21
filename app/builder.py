import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .api.dependencies.auth import (
    get_current_superuser,
    get_current_user
)
from .api.dependencies.auth.markers import (
    CurrentSuperuserMarker,
    CurrentUserMarker
)
from .api.dependencies.markers import (
    AppSettingsMarker,
    DBSessionInTransactionMarker,
    MailSenderMarker,
    OAuthMarker,
    PasswordCryptContextMarker,
    RedisMarker
)
from .api.errors import add_server_error_handler
from .api.routes import router as api_router
from .core.settings import AppSettings
from .core.settings.environment import AppEnvType
from .db import DBState
from .services.mail import MailState
from .services.oauth import OAuthState
from .services.password import PasswordState
from .services.redis_ import RedisState


__all__ = [
    'AppBuilder',
    'get_app'
]

logger = logging.getLogger(__name__)


@dataclass
class AppBuilder:
    settings: AppSettings

    def __post_init__(self) -> None:
        self.app = FastAPI(
            title=self.settings.fastapi_title,
            version=self.settings.fastapi_version,
            docs_url=self.settings.fastapi_docs_url,
            redoc_url=self.settings.fastapi_redoc_url,
            swagger_ui_parameters={'docExpansion': 'none'},
        )

    def build(self) -> FastAPI:
        self._add_middlewares()
        self._add_exception_handlers()
        self._include_routers()
        self._set_lifespan()
        logger.info(f'{self.settings.app_info} has been built.')
        return self.app

    def _add_middlewares(self) -> None:
        self._add_session_middleware()
        self._add_cors_middleware()

    def _add_session_middleware(self) -> None:
        self.app.add_middleware(
            SessionMiddleware,
            secret_key=self.settings.session_secret
        )

    def _add_cors_middleware(self) -> None:
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.cors_origins,
            allow_methods=self.settings.cors_methods,
            allow_headers=self.settings.cors_headers,
            allow_credentials=True,
        )

    def _add_exception_handlers(self) -> None:
        if self.settings.env_type is AppEnvType.DEV:
            add_server_error_handler(self.app)

    def _include_routers(self) -> None:
        self._include_api_router()

    def _include_api_router(self) -> None:
        self.app.include_router(router=api_router)

    def _set_lifespan(self) -> None:
        self.app.router.lifespan_context = self._lifespan

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI) -> AsyncGenerator[None, None]:
        """https://www.starlette.io/events/#registering-events"""
        db = DBState(self.settings.sqlalchemy_url)
        redis = RedisState(self.settings.redis_url)
        mail = MailState(self.settings.mail)
        oauth = OAuthState(self.settings.oauth)
        password = PasswordState()

        deps = app.dependency_overrides
        deps[AppSettingsMarker] = self._depend_on_settings
        deps[CurrentUserMarker] = get_current_user
        deps[CurrentSuperuserMarker] = get_current_superuser
        deps[DBSessionInTransactionMarker] = db
        deps[RedisMarker] = redis
        deps[MailSenderMarker] = mail
        deps[OAuthMarker] = oauth
        deps[PasswordCryptContextMarker] = password

        yield

        await db.shutdown()
        await redis.shutdown()

    def _depend_on_settings(self) -> AppSettings:
        return self.settings


def get_app(settings: AppSettings) -> FastAPI:
    return AppBuilder(settings).build()
