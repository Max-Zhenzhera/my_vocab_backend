from dataclasses import dataclass

from fastapi import Depends
from passlib.context import CryptContext

from .errors import (
    EmailIsAlreadyTakenError,
    IncorrectPasswordError,
    UsernameIsAlreadyTakenError,
    UserWithSuchEmailDoesNotExistError
)
from ...api.dependencies.markers import PasswordCryptContextMarker
from ...db.errors import EntityDoesNotExistError
from ...db.models import User
from ...db.repos import UsersRepo
from ...schemas.user import (
    UserInCreate,
    UserInLogin
)


__all__ = ['UserService']


@dataclass
class UserService:
    repo: UsersRepo = Depends()
    pwd_context: CryptContext = Depends(PasswordCryptContextMarker)

    async def create(self, payload: UserInCreate) -> User:
        if await self.repo.check_email_is_taken(payload.email):
            raise EmailIsAlreadyTakenError
        if await self.repo.check_username_is_taken(payload.username):
            raise UsernameIsAlreadyTakenError
        return await self.raw_create(payload)

    async def raw_create(self, payload: UserInCreate) -> User:
        return await self.repo.create_one(
            **payload.dict(exclude={'password'}),
            hashed_password=self.pwd_context.hash(payload.password)
        )

    async def verify(self, payload: UserInLogin) -> User:
        user = await self.get_for_login(payload.email)
        if not self.pwd_context.verify(payload.password, user.hashed_password):
            raise IncorrectPasswordError
        return user

    async def get_for_login(self, email: str) -> User:
        try:
            user = await self.repo.get_one_by_email(email)
        except EntityDoesNotExistError as error:
            raise UserWithSuchEmailDoesNotExistError from error
        else:
            return user
