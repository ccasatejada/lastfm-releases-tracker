import os


def get_default_user() -> tuple[str | None, str | None]:
    env_username = os.getenv('LASTFM_USERNAME')
    env_password = os.getenv('LASTFM_PASSWORD')
    return env_password, env_username
