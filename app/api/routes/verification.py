import logging

from fastapi import (
    APIRouter,
    Depends
)
from starlette.status import HTTP_200_OK

from ...schemas.verification import VerificationInCreate
from ...services.mail import MailService
from ...services.verification import VerificationService


__all__ = ['router']

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    path='/send',
    name='verification:send',
    summary='Send verification code to email.',
    response_description='Verification code has been sent.',
    status_code=HTTP_200_OK
)
async def send(
    payload: VerificationInCreate,
    verification_service: VerificationService = Depends(),
    mail_service: MailService = Depends()
) -> None:
    """ `Mail: verification.` """
    code = await verification_service.get(payload.email)
    mail_service.send_verification(payload, code)
