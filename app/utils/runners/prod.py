import logging

from ..logging_.config import get_logging_config
from ...core.settings.app import AppProdSettings


__all__ = ['run']

logger = logging.getLogger(__name__)


def run(app_path: str, settings: AppProdSettings) -> None:
    from ..gunicorn_ import StandaloneApplication

    logger.info(
        'Used runner for prod environment [Gunicorn] '
        f'with [{settings.gunicorn_workers_number}] workers.'
    )
    StandaloneApplication(
        app=app_path,
        bind=settings.socket_bind,
        logconfig_dict=get_logging_config(
            app_info=settings.app_info,
            settings=settings.logging
        ),
        workers=settings.gunicorn_workers_number,
        worker_class=settings.gunicorn_worker_class
    ).run()
