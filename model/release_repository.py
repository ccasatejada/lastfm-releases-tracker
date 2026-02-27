import datetime
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Mapped, Session

from model.internal.base_repository import BaseRepository
from model.model import AppUserRelease, Release


class ReleaseRepository(BaseRepository[Release]):
    def __init__(self, session: Session):
        super().__init__(session, Release)

    def update_existing(
        self,
        existing: Release,
        release_date: datetime.date,
        length: int,
        nb_tracks: int,
        release_url: str,
    ) -> None:
        existing.release_date = release_date
        existing.length = length
        existing.nb_tracks = nb_tracks
        existing.release_url = release_url
        self.session.flush()

    def get_by_title(self, artist_id: int, release_title: str) -> Release | None:
        stmt = select(Release).where(
            Release.release_title == release_title, Release.id_artist == artist_id
        )
        return self.session.scalars(stmt).one_or_none()

    def save_all(
        self, all_releases: Sequence[dict], id_artist: Mapped[int], id_user: int
    ) -> None:
        for release_dict in all_releases:
            release_title = release_dict.get('release_title')
            release_date = release_dict.get('release_date')
            release_length = release_dict.get('length')
            nb_tracks = release_dict.get('nb_tracks')
            release_url = release_dict.get('release_url')

            existing = self.get_by_title(id_artist, release_title)

            if existing:
                release = existing
                self.update_existing(
                    existing, release_date, release_length, nb_tracks, release_url
                )
            else:
                release = self.create(
                    release_title=release_title,
                    release_date=release_date,
                    length=release_length,
                    nb_tracks=nb_tracks,
                    release_url=release_url,
                )
            link = self.session.get(AppUserRelease, (id_user, release.id))
            if not link:
                self.session.add(
                    AppUserRelease(
                        id_user=id_user,
                        id_release=release.id,
                    )
                )
            self.session.flush()
            release_dict['id'] = release.id
