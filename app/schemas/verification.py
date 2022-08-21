from pydantic import (
    BaseModel,
    EmailStr
)

from ..db.enums import VerificationAction


__all__ = [
    'VerificationInCreate',
    'VerificationInVerify'
]


class _EmailMixin(BaseModel):
    email: EmailStr


class VerificationInCreate(_EmailMixin):
    action: VerificationAction


class VerificationInVerify(_EmailMixin):
    code: int
