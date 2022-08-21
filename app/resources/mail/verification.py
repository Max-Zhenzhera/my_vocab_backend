from ...db.enums import VerificationAction


ACTION_TO_MESSAGE = {
    VerificationAction.REGISTRATION: (
        'You are just 1 step to get registered. '
        'Please, fill code and become our Dear User!'
    )
}
DEFAULT_ACTION_MESSAGE = (
    'You are trying to do some action '
    'that requires verification. '
    'Please, use current code to proceed.'
)
