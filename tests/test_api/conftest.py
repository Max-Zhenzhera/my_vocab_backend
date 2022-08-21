import asyncio
from collections.abc import (
    AsyncGenerator,
    Callable
)
from contextlib import asynccontextmanager
from os import environ
from typing import (
    Any,
    TypeAlias
)

import pytest
from alembic.command import (
    downgrade as alembic_downgrade,
    upgrade as alembic_upgrade
)
from alembic.config import Config as AlembicConfig
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi_mail import FastMail
from httpx import AsyncClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.markers import (
    DBSessionInTransactionMarker,
    MailSenderMarker,
    PasswordCryptContextMarker,
    RedisMarker
)
from app.builder import get_app
from app.core.config import get_app_settings
from app.core.settings import AppSettings
from app.core.settings.environment import AppEnvType
from app.core.settings.paths import ALEMBIC_CONFIG_PATH
from app.db.models import User
from app.db.repos import UsersRepo
from app.services.auth import UserService
from app.services.jwt_ import (
    JWTBlacklistService,
    JWTService
)
from app.services.redis_ import RedisClient
from app.services.verification import VerificationService
from tests.test_api.dtos import MetaUser


Deps: TypeAlias = dict[Callable[..., Any], Callable[..., Any]]
""" App dependency overrides. """


# environment
# -----------------------------------------------

@pytest.fixture(scope='session', autouse=True)
def set_app_env() -> None:
    environ['APP_ENV'] = AppEnvType.TEST


# loop
# -----------------------------------------------


@pytest.fixture(scope='session')
def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# app initialization
# -----------------------------------------------

@pytest.fixture(scope='session')
def settings() -> AppSettings:
    return get_app_settings(AppEnvType.TEST)


@pytest.fixture(scope='session')
def alembic_config(settings: AppSettings) -> AlembicConfig:
    config = AlembicConfig(str(ALEMBIC_CONFIG_PATH))
    config.set_main_option('sqlalchemy.url', settings.sqlalchemy_url)
    return config


@pytest.fixture(scope='session')
def apply_migrations(alembic_config: AlembicConfig) -> None:
    alembic_upgrade(alembic_config, 'head')
    yield
    alembic_downgrade(alembic_config, 'base')


@pytest.fixture(scope='session')
def prepare_and_cleanup_resources(
    apply_migrations: None
) -> None:
    pass


@pytest.fixture(scope='session')
def app(
    settings: AppSettings,
) -> FastAPI:
    return get_app(settings)


@pytest.fixture(scope='session')
async def initialized_app(
    app: FastAPI,
    prepare_and_cleanup_resources: None
) -> AsyncGenerator[FastAPI, None]:
    async with LifespanManager(app):
        yield app


# dependencies
# -----------------------------------------------

@pytest.fixture(scope='session')
def deps(initialized_app: FastAPI) -> Deps:
    return initialized_app.dependency_overrides


@pytest.fixture(name='db_session')
async def db_session(
    deps: Deps
) -> AsyncGenerator[AsyncSession, None]:
    call = deps[DBSessionInTransactionMarker]
    async with asynccontextmanager(call)() as session:
        yield session


@pytest.fixture
def redis(
    deps: Deps
) -> RedisClient:
    call = deps[RedisMarker]
    return call()


@pytest.fixture
def mail_sender(
    deps: Deps
) -> FastMail:
    call = deps[MailSenderMarker]
    return call()


@pytest.fixture
def pwd_context(
    deps: Deps
) -> CryptContext:
    call = deps[PasswordCryptContextMarker]
    return call()


@pytest.fixture
def verification_service(
    settings: AppSettings,
    redis: RedisClient
) -> VerificationService:
    return VerificationService(
        redis=redis,
        settings=settings
    )


@pytest.fixture
def user_service(
    db_session: AsyncSession,
    pwd_context: CryptContext
) -> UserService:
    return UserService(
        repo=UsersRepo(db_session),
        pwd_context=pwd_context
    )


@pytest.fixture
def jwt_service(
    settings: AppSettings
) -> JWTService:
    return JWTService(settings)


@pytest.fixture
def jwt_blacklist_service(
    settings: AppSettings,
    redis: RedisClient
) -> JWTBlacklistService:
    return JWTBlacklistService(
        redis=redis,
        settings=settings
    )


# users
# -----------------------------------------------

@pytest.fixture
def meta_user_1() -> MetaUser:
    return MetaUser(
        email='user1@gmail.com',
        username='user1Username',
        password='user1Password',
        oauth_id='user1OAuthID12345'
    )


@pytest.fixture
async def user_1(
    user_service: UserService,
    meta_user_1: MetaUser
) -> AsyncGenerator[User, None]:
    user = await user_service.raw_create(meta_user_1.in_create)
    await user_service.repo.session.commit()

    yield user

    await user_service.repo.delete_one_by_pk(user.id)
    await user_service.repo.session.commit()


# clients
# -----------------------------------------------

@pytest.fixture(scope='session')
async def client(
    initialized_app: FastAPI
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        app=initialized_app,
        base_url='http://testserver',
        headers={'Content-Type': 'application/json'},
    ) as client:
        yield client


@pytest.fixture
async def no_auth_client_1(
    user_1: User,
    client: AsyncClient
) -> AsyncClient:
    return client


@pytest.fixture
async def client_1(
    user_1: User,
    jwt_service: JWTService,
    client: AsyncClient
) -> AsyncClient:
    access_token = jwt_service.generate(user_1)
    client.headers['Authorization'] = f'Bearer {access_token}'
    return client


# utils
# -----------------------------------------------

@pytest.fixture
async def flush_redis_db_after_test(
    redis: RedisClient
) -> AsyncGenerator[None, None]:
    yield
    await redis.flushdb()


@pytest.fixture
async def delete_all_users_after_test(
    db_session: AsyncSession
) -> AsyncGenerator[None, None]:
    yield
    await UsersRepo(db_session).delete_all()
    await db_session.commit()
