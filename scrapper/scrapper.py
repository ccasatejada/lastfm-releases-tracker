from collections.abc import Callable

import requests

from constant.constant import BASE_URL
from model.model import AppUser
from scrapper.internal.fetcher import ArtistsFetcher, BaseFetcher, ReleasesFetcher
from service import user_service


def init_user(lastfm_username: str) -> AppUser:
    url = f'{BASE_URL}/fr/user/{lastfm_username}'
    response = requests.get(url)

    if response.status_code == 404:
        raise ValueError(f'Last.fm user "{lastfm_username}" does not exist')
    response.raise_for_status()

    return user_service.create_user(lastfm_username)


def fetch_artists(
    lastfm_username: str,
    lastfm_password: str,
    on_artist_fetched: Callable[[str, int], None] | None = None,
) -> None:
    fetcher = ArtistsFetcher(lastfm_username, lastfm_password)
    fetcher.fetch(on_artist_fetched)


def fetch_releases(
    lastfm_username: str,
    lastfm_password: str,
    id_artist: int,
    on_release_fetched: Callable[[str, int], None] | None = None,
    http_session: requests.Session = None,
) -> None:
    fetcher = ReleasesFetcher(lastfm_username, lastfm_password, id_artist, http_session)
    fetcher.fetch(on_release_fetched)


def fetch_all_releases(
    lastfm_username: str,
    lastfm_password: str,
    on_release_fetched: Callable[[str, int], None] | None = None,
) -> None:
    user = user_service.get_user(lastfm_username)
    artists = user_service.get_user_artists(user.id)

    _base = BaseFetcher(lastfm_username, lastfm_password)

    for artist_id, _artist_name in artists:
        fetch_releases(
            lastfm_username,
            lastfm_password,
            artist_id,
            on_release_fetched,
            _base.get_http_session(),
        )
