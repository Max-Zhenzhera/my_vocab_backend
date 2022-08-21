from enum import Enum


__all__ = ['OAuthBackend']


class OAuthBackend(str, Enum):
    """ Note: used in url as `Path` params. """
    GOOGLE = 'google'
    DISCORD = 'discord'
