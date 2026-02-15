from typing import Callable

import requests

from constant.constant import BASE_URL
from db.database import get_session
from model.app_user_repository import AppUserRepository
from model.model import AppUser
from scrapper.internal.fetcher import ArtistsFetcher


def init_user(lastfm_username: str) -> AppUser:
    url = f'{BASE_URL}/fr/user/{lastfm_username}'
    response = requests.get(url)

    if response.status_code == 404:
        raise ValueError(f'Last.fm user "{lastfm_username}" does not exist')
    response.raise_for_status()

    with get_session() as session:
        repo = AppUserRepository(session)

        existing = repo.get_by_lastfm_username(lastfm_username)
        if existing:
            return existing

        return repo.create(lastfm_username=lastfm_username)

def fetch_artists(lastfm_username: str,
                  lastfm_password: str,
                  on_artist_fetched: Callable[[str, int], None] | None = None) -> None:
    fetcher = ArtistsFetcher(lastfm_username, lastfm_password)
    fetcher.fetch(on_artist_fetched)

