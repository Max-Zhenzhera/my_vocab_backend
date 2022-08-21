from os import environ
from typing import ClassVar

from fastapi_mail.config import ConnectionConfig as MailSettings
from pydantic import (
    BaseSettings,
    Field,
    PostgresDsn,
    RedisDsn
)

from ..environment import AppEnvType
from ..paths import EMAIL_TEMPLATES_DIR
from ....db.enums import OAuthBackend


__all__ = ['AppSettings']


class AppSettings(BaseSettings):
    project_name: ClassVar[str] = 'My Vocab Backend'
    env_type: AppEnvType = Field(..., env='APP_ENV')

    socket_host: str = Field('127.0.0.1', env='APP_HOST')
    socket_port: int = Field(8000, env='APP_PORT')

    fastapi_title: str = Field(project_name, env='APP_TITLE')
    fastapi_version: str = Field('0.1.0', env='APP_VERSION')
    fastapi_docs_url: str = Field('/docs', env='APP_DOCS_URL')
    fastapi_redoc_url: str = Field('/redoc', env='APP_REDOC_URL')

    cors_origins: list[str] = Field(..., env='CORS_ORIGINS')
    cors_methods: list[str] = Field(..., env='CORS_METHODS')
    cors_headers: list[str] = Field(..., env='CORS_HEADERS')

    session_secret: str = Field(..., env='SESSION_SECRET')

    db_dialect: ClassVar[str] = 'postgresql'
    db_driver: ClassVar[str] = 'asyncpg'
    db_url: PostgresDsn = Field(..., env='DB_URL')

    redis_url: RedisDsn = Field(..., env='REDIS_URL')

    jwt_algorithm: ClassVar[str] = 'HS256'
    jwt_secret: str = Field(..., env='JWT_SECRET')

    mail_username: str = Field(..., env='MAIL_USERNAME')
    mail_password: str = Field(..., env='MAIL_PASSWORD')
    mail_server: str = Field(..., env='MAIL_SERVER')
    mail_port: int = Field(..., env='MAIL_PORT')
    mail_tls: bool = Field(True, env='MAIL_TLS')
    mail_ssl: bool = Field(False, env='MAIL_SSL')
    mail_from: str = Field(..., env='MAIL_FROM')
    mail_from_name: str = Field(..., env='MAIL_FROM_NAME')
    mail_suppress_send: bool = Field(False, env='MAIL_SUPPRESS_SEND')

    access_token_expire_in_seconds: int = Field(
        ...,
        env='ACCESS_TOKEN_EXPIRE_IN_SECONDS'
    )
    refresh_token_expire_in_seconds: int = Field(
        ...,
        env='REFRESH_TOKEN_EXPIRE_IN_SECONDS'
    )
    verification_code_expire_in_seconds: int = Field(
        ...,
        env='VERIFICATION_CODE_EXPIRE_IN_SECONDS'
    )

    @property
    def app_info(self) -> str:
        return (
            f'{self.fastapi_title} '
            f'({self.fastapi_version}) '
            f'[{self.env_type}]'
        )

    @property
    def socket_bind(self) -> str:
        return f'{self.socket_host}:{self.socket_port}'

    @property
    def sqlalchemy_scheme(self) -> str:
        return f'{self.db_dialect}+{self.db_driver}'

    @property
    def sqlalchemy_url(self) -> str:
        if self.sqlalchemy_scheme in self.db_url:
            return self.db_url
        return self.db_url.replace(self.db_dialect, self.sqlalchemy_scheme)

    @property
    def mail(self) -> MailSettings:
        return MailSettings(
            MAIL_USERNAME=self.mail_username,
            MAIL_PASSWORD=self.mail_password,
            MAIL_SERVER=self.mail_server,
            MAIL_PORT=self.mail_port,
            MAIL_TLS=self.mail_tls,
            MAIL_SSL=self.mail_ssl,
            MAIL_FROM=self.mail_from,
            MAIL_FROM_NAME=self.mail_from_name,
            SUPPRESS_SEND=self.mail_suppress_send,
            TEMPLATE_FOLDER=EMAIL_TEMPLATES_DIR
        )

    @property
    def oauth(self) -> dict[str, str]:
        backends = {backend.upper() for backend in OAuthBackend}
        params = {'CLIENT_ID', 'CLIENT_SECRET'}
        config = {}
        for backend in backends:
            for param in params:
                key = f'{backend}_{param}'
                config[key] = environ.get(key, '')
        return config
