from dataclasses import dataclass


__all__ = [
    'TGLoggingSettings',
    'LoggingSettings'
]


@dataclass
class TGLoggingSettings:
    use: bool
    token: str
    admins: list[str]


@dataclass
class LoggingSettings:
    level: str
    tg: TGLoggingSettings
