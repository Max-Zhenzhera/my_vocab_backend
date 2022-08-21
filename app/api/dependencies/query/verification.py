from fastapi import Query

from ....services.verification import VERIFICATION_CODES_RANGE


__all__ = ['VerificationCodeQuery']


VerificationCodeQuery = Query(
    ...,
    gt=VERIFICATION_CODES_RANGE.start - 1,
    lt=VERIFICATION_CODES_RANGE.stop
)
