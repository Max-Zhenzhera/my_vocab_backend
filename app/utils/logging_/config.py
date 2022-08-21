import logging
import logging.config
from typing import Any

from .filters import StdoutFilter
from .handlers import TGHandler
from ...core.settings.dataclasses_ import LoggingSettings


__all__ = [
    'configure_base_logging',
    'get_logging_config'
]

logger = logging.getLogger(__name__)


def configure_base_logging() -> None:
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        # Formatters
        # ---------------------------------------
        'formatters': {
            'standard': {
                'style': '{',
                'format': (
                    '[{asctime}] [{process}] [{levelname}] '
                    '{name}: {message}'
                ),
                'datefmt': '%Y-%m-%d %H:%M:%S %z'
            }
        },
        # Filters
        # ---------------------------------------
        'filters': {
            'StdoutFilter': {
                '()': StdoutFilter
            }
        },
        # Handlers
        # ---------------------------------------
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': logging.DEBUG,
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
                'filters': ['StdoutFilter']
            },
            'error_console': {
                'class': 'logging.StreamHandler',
                'level': logging.WARNING,
                'formatter': 'standard',
                'stream': 'ext://sys.stderr'
            }
        },
        # Root logger
        # ---------------------------------------
        'root': {
            'level': logging.INFO,
            'handlers': [
                'console',
                'error_console'
            ]
        }
    }
    logging.config.dictConfig(config)


def get_logging_config(
    app_info: str,
    settings: LoggingSettings
) -> dict[str, Any]:
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        # Formatters
        # ---------------------------------------
        'formatters': {
            'standard': {
                'style': '{',
                'format': (
                    '[{asctime}] [{process}] [{levelname}] '
                    '{name}: {message}'
                ),
                'datefmt': '%Y-%m-%d %H:%M:%S %z'
            },
            'detailed': {
                'style': '{',
                'format': (
                    '[{asctime}] [{process}] [{levelname}] '
                    '{name} - {funcName}()[{lineno}]: {message}'
                ),
                'datefmt': '%Y-%m-%d %H:%M:%S %z'
            }
        },
        # Filters
        # ---------------------------------------
        'filters': {
            'StdoutFilter': {
                '()': StdoutFilter
            }
        },
        # Handlers
        # ---------------------------------------
        'handlers': {
            'server_console': {
                'class': 'logging.StreamHandler',
                'level': logging.DEBUG,
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
                'filters': ['StdoutFilter']
            },
            'server_error_console': {
                'class': 'logging.StreamHandler',
                'level': logging.WARNING,
                'formatter': 'standard',
                'stream': 'ext://sys.stderr'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': logging.DEBUG,
                'formatter': 'detailed',
                'stream': 'ext://sys.stdout',
                'filters': ['StdoutFilter']
            },
            'error_console': {
                'class': 'logging.StreamHandler',
                'level': logging.WARNING,
                'formatter': 'detailed',
                'stream': 'ext://sys.stderr'
            }
        },
        # Root logger
        # ---------------------------------------
        'root': {
            'level': settings.level,
            'handlers': [
                'console',
                'error_console'
            ]
        },
        # Loggers
        # ---------------------------------------
        'loggers': {
            'sqlalchemy': {
                'level': logging.INFO,
                'propagate': True
            },
            'gunicorn.access': {
                'level': logging.INFO,
                'handlers': [
                    'server_console',
                    'server_error_console'
                ],
                'propagate': False
            },
            'gunicorn.error': {
                'level': logging.INFO,
                'handlers': [
                    'server_console',
                    'server_error_console'
                ],
                'propagate': False
            },
            'uvicorn.access': {
                'level': logging.INFO,
                'handlers': [
                    'server_console',
                    'server_error_console'
                ],
                'propagate': False
            },
            'uvicorn.error': {
                'level': logging.INFO,
                'handlers': [
                    'server_console',
                    'server_error_console'
                ],
                'propagate': False
            }
        }
    }

    if settings.tg.use:
        tg_handler_name = 'tg_handler'
        config['handlers'][tg_handler_name] = {  # type: ignore[index]
            '()': TGHandler,
            'level': logging.ERROR,
            'app_info': app_info,
            'settings': settings.tg,
            'formatter': 'detailed'
        }
        loggers_to_append_tg_handler = (
            config['root'],
            config['loggers']['gunicorn.access'],  # type: ignore[index]
            config['loggers']['gunicorn.error'],  # type: ignore[index]
            config['loggers']['uvicorn.access'],  # type: ignore[index]
            config['loggers']['uvicorn.error']  # type: ignore[index]
        )
        for logger_ in loggers_to_append_tg_handler:
            logger_['handlers'].append(tg_handler_name)

    return config
