from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Mapped

from db.database import get_session
from model.model import AppUserRelease, Release
from model.release_repository import ReleaseRepository


def save_releases(
    all_releases: Sequence[dict], id_artist: Mapped[int], id_user: int
) -> None:
    with get_session() as session:
        repo = ReleaseRepository(session)

        for release_dict in all_releases:
            release_title = release_dict.get('release_title')
            release_date = release_dict.get('release_date')
            release_length = release_dict.get('length')
            nb_tracks = release_dict.get('nb_tracks')
            release_url = release_dict.get('release_url')

            existing = session.scalar(
                select(Release).where(
                    Release.release_title == release_title,
                    Release.id_artist == id_artist,
                )
            )
            if existing:
                release = existing
                release.release_date = release_date
                release.length = release_length
                release.nb_tracks = nb_tracks
                release.release_url = release_url
            else:
                release = repo.create(
                    release_title=release_title,
                    release_date=release_date,
                    length=release_length,
                    nb_tracks=nb_tracks,
                    release_url=release_url,
                    id_artist=id_artist,
                )

            link = session.get(AppUserRelease, (id_user, release.id))
            if not link:
                session.add(
                    AppUserRelease(
                        id_user=id_user,
                        id_release=release.id,
                    )
                )
            session.flush()

            release_dict['id'] = release.id
