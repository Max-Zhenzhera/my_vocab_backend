from dataclasses import dataclass

from fastapi import Request


__all__ = ['ClientAnalyzer']


@dataclass
class ClientAnalyzer:
    request: Request

    @property
    def ip_address(self) -> str:
        if (address := self.request.client) is not None:
            return address.host
        return ''

    @property
    def user_agent(self) -> str:
        return self.request.headers['user-agent']
