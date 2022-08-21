import logging
from io import BytesIO
from logging import LogRecord
from typing import Any

import httpx
from httpx import (
    HTTPError,
    Response
)
from starlette.status import HTTP_200_OK

from ....core.settings.dataclasses_ import TGLoggingSettings


__all__ = ['TGHandler']

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)
logger.propagate = False

API_ENDPOINT = 'https://api.telegram.org'


class TGHandler(logging.Handler):
    def __init__(
        self,
        app_info: str,
        settings: TGLoggingSettings
    ) -> None:
        self._app_info = app_info
        self._settings = settings
        super().__init__()

    def emit(self, record: LogRecord) -> None:
        text = self.format(record)

        for admin in self._settings.admins:
            self._send_document(
                chat_id=admin,
                document=BytesIO(text.encode())
            )

    def _send_document(self, chat_id: str, document: BytesIO) -> Response | None:
        return self._request(
            method='sendDocument',
            data={
                'chat_id': chat_id,
                'caption': self._app_info
            },
            files={'document': ('traceback.txt', document, 'text/plain')}
        )

    def _request(self, method: str, **kwargs: Any) -> Response | None:
        url = self._format_url(method)

        try:
            response = httpx.post(url, **kwargs)
        except HTTPError as error:
            logger.exception(
                f'Error on TG API request [{url}].',
                exc_info=error
            )
            return None
        else:
            if response.status_code != HTTP_200_OK:
                logger.error(f'Unsuccessful TG API request: {response.status_code=}.')
            return response

    def _format_url(self, method: str) -> str:
        return f'{API_ENDPOINT}/bot{self._settings.token}/{method}'
