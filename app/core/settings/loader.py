import logging
from os import environ

from dotenv import (
    find_dotenv,
    load_dotenv
)

from .environment import (
    ENV_FILES,
    AppEnvType
)


__all__ = [
    'recognize_app_environment_type',
    'load_app_environment'
]

logger = logging.getLogger(__name__)


def recognize_app_environment_type() -> AppEnvType:
    load_dotenv()
    app_env = environ['APP_ENV']
    try:
        env_type = AppEnvType(app_env.lower())
    except ValueError as error:
        env_types = ''.join(
            f'\n\t - {env_type!r}' for env_type in AppEnvType
        )
        raise ValueError(
            f'Possible values for `APP_ENV` are: {env_types}'
        ) from error
    else:
        logger.debug(f'{env_type!r} has been parsed from [environment/.env].')
        return env_type


def load_app_environment(env_type: AppEnvType) -> None:
    env_filename = ENV_FILES[env_type]
    load_dotenv(find_dotenv(env_filename))
    logger.info(f'{env_type!r} [{env_filename}] has been loaded.')
