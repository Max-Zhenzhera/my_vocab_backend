import logging
import warnings
from dataclasses import dataclass

from fastapi_mail import (
    ConnectionConfig as MailConnectionSettings,
    FastMail
)


__all__ = ['MailState']


logger = logging.getLogger(__name__)


@dataclass
class MailState:
    settings: MailConnectionSettings

    def __post_init__(self) -> None:
        self.sender = FastMail(self.settings)
        logger.info('Mail state (sender) has been set.')

        if self.settings.SUPPRESS_SEND:
            warnings.warn(
                'Mail sending is suppressed by configuration.',
                UserWarning
            )

    def __call__(self) -> FastMail:
        return self.sender
