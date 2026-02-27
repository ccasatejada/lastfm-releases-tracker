from collections.abc import Sequence
from typing import Any

from db.database import get_session
from model.artist_repository import ArtistRepository
from model.model import AppUser, Artist, Release


def save_artists(all_artists: Sequence[dict], id_user: int) -> None:
    with get_session() as session:
        repo = ArtistRepository(session)
        repo.save_all(all_artists, id_user)


def get_all_artists_with_counts() -> list[Any]:
    """Returns list of (id, artist_name, nb_releases, nb_users, created_at, updated_at)."""
    with get_session() as session:
        repo = ArtistRepository(session)
        return repo.get_all_artists_with_counts()


def get_artist(id_artist: int) -> Artist | None:
    with get_session() as session:
        repo = ArtistRepository(session)
        return repo.get(id_artist)


def get_artist_detail(
    id_artist: int,
) -> tuple[Artist | None, list[AppUser], list[Release]]:
    """Returns (artist, users, releases) for the given artist."""
    with get_session() as session:
        repo = ArtistRepository(session)
        artist = repo.get(id_artist)
        users = repo.get_users(id_artist)

        releases = sorted(artist.releases, key=lambda r: r.release_date, reverse=True)

        return artist, users, releases
