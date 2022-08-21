from authlib.oidc.core.claims import UserInfo

from ...db.enums import OAuthBackend
from ...dtos.oauth import OAuthUser


__all__ = ['USERINFO_CASTERS']


def cast_google_userinfo(userinfo: UserInfo) -> OAuthUser:
    return OAuthUser(
        id=userinfo['sub'],
        email=userinfo['email'],
        detail=userinfo['name']
    )


def cast_discord_userinfo(userinfo: UserInfo) -> OAuthUser:
    return OAuthUser(
        id=userinfo['id'],
        email=userinfo['email'],
        detail=f'{userinfo["username"]}#{userinfo["discriminator"]}'
    )


USERINFO_CASTERS = {
    OAuthBackend.GOOGLE: cast_google_userinfo,
    OAuthBackend.DISCORD: cast_discord_userinfo
}
