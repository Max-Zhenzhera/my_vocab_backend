import logging
import warnings
from dataclasses import dataclass

from fastapi import (
    BackgroundTasks,
    Depends
)
from fastapi_mail import (
    FastMail,
    MessageSchema
)

from ...api.dependencies.markers import MailSenderMarker
from ...resources.mail.subjects import (
    SUBJECT_FOR_THANK,
    SUBJECT_FOR_VERIFICATION
)
from ...resources.mail.verification import (
    ACTION_TO_MESSAGE,
    DEFAULT_ACTION_MESSAGE
)
from ...schemas.user import UserInResponse
from ...schemas.verification import VerificationInCreate


__all__ = ['MailService']

warnings.warn(
    'Emails will be built for the LOCAL DEVELOPMENT. '
    'For production: programmer has to provide a new implementation!',
    UserWarning
)

logger = logging.getLogger(__name__)


@dataclass
class MailService:
    background_tasks: BackgroundTasks
    mail_sender: FastMail = Depends(MailSenderMarker)

    def send_verification(
        self,
        payload: VerificationInCreate,
        code: str
    ) -> None:
        self.background_tasks.add_task(
            self.mail_sender.send_message,
            message=MessageSchema(
                subject=SUBJECT_FOR_VERIFICATION,
                recipients=[payload.email],
                template_body={
                    'code': code,
                    'message': ACTION_TO_MESSAGE.get(
                        payload.action,
                        DEFAULT_ACTION_MESSAGE
                    )
                }
            ),
            template_name='verification.html'
        )
        logger.info(
            f'Verification mail sending for {payload.email} '
            'has been pushed in background tasks.'
        )

    def send_thank_for_registering(self, user: UserInResponse) -> None:
        self.background_tasks.add_task(
            self.mail_sender.send_message,
            message=MessageSchema(
                subject=SUBJECT_FOR_THANK,
                recipients=[user.email],
                template_body={'user': user},
            ),
            template_name='thank.html'
        )
        logger.info(
            f'Thank mail sending for {user.email} '
            'has been pushed in background tasks.'
        )
