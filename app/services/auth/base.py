from abc import (
    ABC,
    abstractmethod
)
from typing import Any


__all__ = [
    'BaseAuthService',
    'BaseServerAuthService'
]


class BaseAuthService(ABC):
    @abstractmethod
    async def register(self, *args: Any, **kwargs: Any) -> Any:
        """ Register a new user. """

    @abstractmethod
    async def login(self, *args: Any, **kwargs: Any) -> Any:
        """ Login the existed user. """


class BaseServerAuthService(BaseAuthService):
    @abstractmethod
    async def refresh(self, *args: Any, **kwargs: Any) -> Any:
        """ Refresh the user`s session. """
