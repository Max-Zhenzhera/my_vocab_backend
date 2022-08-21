from enum import Enum


__all__ = ['VerificationAction']


class VerificationAction(str, Enum):
    REGISTRATION = 'registration'
