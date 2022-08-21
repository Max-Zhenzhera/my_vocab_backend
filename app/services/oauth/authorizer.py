from collections.abc import Callable
from dataclasses import dataclass

from authlib.integrations.starlette_client import (
    OAuth,
    StarletteOAuth2App
)
from authlib.oauth2.rfc6749 import OAuth2Token
from authlib.oidc.core.claims import UserInfo
from fastapi import (
    Depends,
    Request
)

from .mixins import CtxOAuthBackendMixin
from .userinfo_ import USERINFO_CASTERS
from ...api.dependencies.markers import OAuthMarker
from ...dtos.oauth import OAuthUser


__all__ = ['OAuthAuthorizer']


@dataclass
class OAuthAuthorizer(CtxOAuthBackendMixin):
    request: Request
    oauth: OAuth = Depends(OAuthMarker)

    @property
    def client(self) -> StarletteOAuth2App:
        return self.oauth.create_client(self.backend)

    async def get_oauth_user(self) -> OAuthUser:
        userinfo = await self.get_userinfo()
        return self.get_userinfo_caster()(userinfo)

    async def get_userinfo(self) -> UserInfo:
        token: OAuth2Token = await self.client.authorize_access_token(self.request)
        if (userinfo := token.get('userinfo')) is not None:
            return userinfo
        return await self.client.userinfo(token=token)

    def get_userinfo_caster(self) -> Callable[[UserInfo], OAuthUser]:
        return USERINFO_CASTERS[self.backend]
