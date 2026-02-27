from collections.abc import Sequence

from sqlalchemy.orm import Mapped

from db.database import get_session
from model.release_repository import ReleaseRepository


def save_releases(
    all_releases: Sequence[dict], id_artist: Mapped[int], id_user: int
) -> None:
    with get_session() as session:
        repo = ReleaseRepository(session)
        repo.save_all(all_releases, id_artist, id_user)
