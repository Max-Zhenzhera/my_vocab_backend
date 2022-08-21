from passlib.context import CryptContext


__all__ = ['PasswordState']


class PasswordState:
    def __init__(self) -> None:
        self.pwd_context = CryptContext(
            schemes=['bcrypt'],
            deprecated='auto'
        )

    def __call__(self) -> CryptContext:
        return self.pwd_context
