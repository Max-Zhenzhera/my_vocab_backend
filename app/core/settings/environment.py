from enum import Enum


__all__ = [
    'AppEnvType',
    'ENV_FILES'
]


class AppEnvType(str, Enum):
    PROD = 'prod'
    DEV = 'dev'
    TEST = 'test'


ENV_FILES = {
    environment: f'.env.{environment}'
    for environment in AppEnvType
}
