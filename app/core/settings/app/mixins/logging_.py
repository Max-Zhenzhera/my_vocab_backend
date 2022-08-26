from typing import Any

from pydantic import (
    BaseSettings,
    Field,
    root_validator,
    validator
)

from ...dataclasses_ import (
    LoggingSettings,
    TGLoggingSettings
)


__all__ = ['LoggingSettingsMixin']


class LoggingSettingsMixin(BaseSettings):
    logging_level: str = Field('INFO', env='LOGGING_LEVEL')

    logging_tg_use: bool = Field(True, env='LOGGING_TG_USE')
    logging_tg_token: str = Field('', env='LOGGING_TG_TOKEN')
    logging_tg_admins: list[str] = Field(
        default_factory=list,
        env='LOGGING_TG_ADMINS'
    )

    @root_validator
    def tg_settings_present_if_use_checked(
        cls,
        values: dict[str, Any]
    ) -> dict[str, Any]:
        if not (use := values['logging_tg_use']):
            return values
        admins, token = values['logging_tg_admins'], values['logging_tg_token']
        assert all([use, admins, token]), (
            'If `LOGGING_TG_USE` is checked, '
            '`LOGGING_TG_TOKEN` and `LOGGING_TG_ADMINS` must be passed too.'
        )
        return values

    @validator('logging_tg_token')
    def tg_token_meets_common_pattern(cls, token: str) -> str:
        """ https://github.com/aiogram/aiogram/blob/dev-3.x/aiogram/utils/token.py """
        if not token:
            return token
        assert all(not char.isspace() for char in token), (
            "`LOGGING_TG_TOKEN` is invalid! It can't contains spaces."
        )
        left, sep, right = token.partition(':')
        assert sep and left.isdigit() and right, (
            '`LOGGING_TG_TOKEN` is invalid.'
        )
        return token

    @property
    def logging(self) -> LoggingSettings:
        return LoggingSettings(
            level=self.logging_level,
            tg=self._logging_tg
        )

    @property
    def _logging_tg(self) -> TGLoggingSettings:
        return TGLoggingSettings(
            use=self.logging_tg_use,
            token=self.logging_tg_token,
            admins=self.logging_tg_admins
        )
