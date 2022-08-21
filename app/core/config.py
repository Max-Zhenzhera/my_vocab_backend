import logging

from .settings import AppSettings
from .settings.app import (
    AppDevSettings,
    AppProdSettings,
    AppTestSettings
)
from .settings.environment import AppEnvType
from .settings.loader import (
    load_app_environment,
    recognize_app_environment_type
)


__all__ = [
    'ENVIRONMENTS',
    'get_app_settings'
]

logger = logging.getLogger(__name__)

ENVIRONMENTS = {
    AppEnvType.PROD: AppProdSettings,
    AppEnvType.DEV: AppDevSettings,
    AppEnvType.TEST: AppTestSettings
}


def get_app_settings(env_type: AppEnvType | None = None) -> AppSettings:
    env_type = env_type or recognize_app_environment_type()
    load_app_environment(env_type)
    return ENVIRONMENTS[env_type](env_type=env_type)  # type: ignore[no-any-return]
