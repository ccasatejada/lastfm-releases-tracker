from collections.abc import Sequence
from typing import Any

from sqlalchemy.orm import Mapped

from db.database import get_session
from model.model import AppUserRelease, Artist, Release
from model.release_repository import ReleaseRepository


def save_releases(
    all_releases: Sequence[dict], id_artist: Mapped[int], id_user: int
) -> None:
    with get_session() as session:
        repo = ReleaseRepository(session)
        repo.save_all(all_releases, id_artist, id_user)


def get_all_releases() -> list[Any]:
    """Returns list of (id, artist_name, title, date, length, nb_tracks, url) ordered by date DESC."""
    with get_session() as session:
        repo = ReleaseRepository(session)
        return repo.get_all_with_artist()


def get_release_detail(
    id_release: int,
) -> tuple[Release | None, Artist, list[AppUserRelease]]:
    """Returns (release, artist, user_releases) for the given release."""
    with get_session() as session:
        repo = ReleaseRepository(session)
        return repo.get_with_artist_and_users(id_release)
