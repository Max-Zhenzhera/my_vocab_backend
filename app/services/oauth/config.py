from ...db.enums import OAuthBackend


__all__ = ['BACKENDS_CONFIG']

GOOGLE_CONFIG = {
    'server_metadata_url': (
        'https://accounts.google.com/.well-known/openid-configuration'
    ),
    'client_kwargs': {'scope': 'openid email profile'},
}
DISCORD_CONFIG = {
    'api_base_url': 'https://discordapp.com/api/',
    'access_token_url': 'https://discordapp.com/api/oauth2/token',
    'authorize_url': 'https://discordapp.com/api/oauth2/authorize',
    'userinfo_endpoint': 'https://discordapp.com/api/users/%40me',
    'client_kwargs': {
        'token_endpoint_auth_method': 'client_secret_post',
        'scope': 'identify email'
    }
}
BACKENDS_CONFIG = {
    OAuthBackend.GOOGLE: GOOGLE_CONFIG,
    OAuthBackend.DISCORD: DISCORD_CONFIG
}
