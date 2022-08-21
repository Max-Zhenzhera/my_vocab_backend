import logging

from ..logging_.config import get_logging_config
from ...core.settings.app import AppDevSettings


__all__ = ['run']

logger = logging.getLogger(__name__)


def run(app_path: str, settings: AppDevSettings) -> None:
    import uvicorn

    logger.info('Used runner for dev environment [Uvicorn].')
    uvicorn.run(
        app=app_path,
        host=settings.socket_host,
        port=settings.socket_port,
        log_config=get_logging_config(
            app_info=settings.app_info,
            settings=settings.logging
        ),
        reload=settings.uvicorn_reload
    )
