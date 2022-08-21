import traceback
import warnings

from fastapi import (
    FastAPI,
    Request
)
from fastapi.responses import PlainTextResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


__all__ = [
    'server_error_handler',
    'add_server_error_handler'
]


def server_error_handler(
    _: Request,
    exception: Exception
) -> PlainTextResponse:
    """ Return the traceback of the internal server error. """
    exception_traceback = ''.join(
        traceback.format_exception(
            type(exception),
            value=exception,
            tb=exception.__traceback__
        )
    )
    message = (
        f'{"Internal server error has occurred.":<50}|\n'
        f'{"Please, check the traceback.":<50}|\n'
        f'{"-" * 50}x\n\n'
    )
    message += exception_traceback
    return PlainTextResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=message
    )


def add_server_error_handler(app: FastAPI) -> None:
    app.add_exception_handler(Exception, server_error_handler)
    warnings.warn(
        'Exception handler that shows traceback on internal server error '
        'has been added.',
        UserWarning
    )
