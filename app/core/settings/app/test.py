from pydantic import (
    Field,
    RedisDsn
)

from .base import AppSettings


__all__ = ['AppTestSettings']


class AppTestSettings(AppSettings):
    cors_origins: list[str] = Field(['*'], env='CORS_ORIGINS')
    cors_methods: list[str] = Field(['*'], env='CORS_METHODS')
    cors_headers: list[str] = Field(['*'], env='CORS_HEADERS')

    session_secret: str = Field('fakeSessionSecret', env='SESSION_SECRET')

    redis_url: RedisDsn = Field('redis://localhost', env='REDIS_URL')

    jwt_secret: str = Field('fakeJWTSecret', env='JWT_SECRET')

    mail_username: str = Field('test@myvocab.com', env='MAIL_USERNAME')
    mail_password: str = Field('fakeMailPassword', env='MAIL_PASSWORD')
    mail_server: str = Field('smtp.myvocab.com', env='MAIL_SERVER')
    mail_port: int = Field(587, env='MAIL_PORT')
    mail_tls: bool = Field(True, env='MAIL_TLS')
    mail_ssl: bool = Field(False, env='MAIL_SSL')
    mail_from: str = Field('test@myvocab.com', env='MAIL_FROM')
    mail_from_name: str = Field('My Vocab App In Test', env='MAIL_FROM_NAME')
    mail_suppress_send: bool = Field(True, env='MAIL_SUPPRESS_SEND')

    access_token_expire_in_seconds: int = Field(
        6_000,
        env='ACCESS_TOKEN_EXPIRE_IN_SECONDS'
    )
    refresh_token_expire_in_seconds: int = Field(
        60_000,
        env='ACCESS_TOKEN_EXPIRE_IN_SECONDS'
    )

    verification_code_expire_in_seconds: int = Field(
        6_000,
        env='VERIFICATION_CODE_EXPIRE_IN_SECONDS'
    )
