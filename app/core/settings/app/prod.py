from typing import ClassVar

from pydantic import Field

from .base import AppSettings
from .mixins import LoggingSettingsMixin


__all__ = ['AppProdSettings']


class AppProdSettings(
    LoggingSettingsMixin,
    AppSettings
):
    gunicorn_worker_class: ClassVar[str] = 'uvicorn.workers.UvicornWorker'
    gunicorn_workers_number: int = Field(1, env='GUNICORN_WORKERS_NUMBER')
