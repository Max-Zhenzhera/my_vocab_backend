from pydantic import Field

from .base import AppSettings
from .mixins import LoggingSettingsMixin


__all__ = ['AppDevSettings']


class AppDevSettings(
    LoggingSettingsMixin,
    AppSettings
):
    uvicorn_reload: bool = Field(False, env='UVICORN_RELOAD')
