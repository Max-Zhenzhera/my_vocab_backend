from typing import ClassVar

from .base import BaseRepo
from ..models import User


__all__ = ['UsersRepo']


class UsersRepo(BaseRepo[User]):
    model: ClassVar = User

    async def get_one_by_email(self, email: str) -> User:
        return await self.get_one([User.email == email])

    async def check_email_is_taken(self, email: str) -> bool:
        return await self.exists([User.email == email])

    async def check_username_is_taken(self, username: str) -> bool:
        return await self.exists([User.username == username])
