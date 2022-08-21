from typing import cast

from .dev import run as run_dev
from .prod import run as run_prod
from ...core.settings import AppSettings
from ...core.settings.app import (
    AppDevSettings,
    AppProdSettings
)
from ...core.settings.environment import AppEnvType


__all__ = ['run']


def run(app_path: str, settings: AppSettings) -> None:
    """ To help mypy check call signatures - make it verbose. """
    if settings.env_type is AppEnvType.PROD:
        settings = cast(AppProdSettings, settings)
        run_prod(app_path, settings)
    else:
        settings = cast(AppDevSettings, settings)
        run_dev(app_path, settings)
