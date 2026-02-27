from collections.abc import Sequence
from typing import Any

from sqlalchemy import Row, func, select
from sqlalchemy.orm import Session, selectinload

from model.internal.base_repository import BaseRepository
from model.model import AppUser, AppUserArtist, Artist, Release


class ArtistRepository(BaseRepository[Artist]):
    def __init__(self, session: Session):
        super().__init__(session, Artist)

    def search_by_name(self, name: str) -> list[Artist]:
        """Recherche des artistes par nom (LIKE)"""
        stmt = select(Artist).where(Artist.artist_name.ilike(f'%{name}%'))
        return list(self.session.scalars(stmt))

    def get_with_releases(self, artist_id: int) -> Artist | None:
        """Récupère un artiste avec ses releases"""
        stmt = (
            select(Artist)
            .where(Artist.id == artist_id)
            .options(selectinload(Artist.releases))
        )
        return self.session.scalar(stmt)

    def get_all_artists_with_counts(self) -> list[Any]:
        stmt = (
            select(
                Artist.id,
                Artist.artist_name,
                func.count(func.distinct(Release.id)).label('nb_releases'),
                func.count(func.distinct(AppUserArtist.id_user)).label('nb_users'),
                Artist.created_at,
                Artist.updated_at,
            )
            .outerjoin(Release, Release.id_artist == Artist.id)
            .outerjoin(AppUserArtist, AppUserArtist.id_artist == Artist.id)
            .group_by(
                Artist.id, Artist.artist_name, Artist.created_at, Artist.updated_at
            )
            .order_by(Artist.artist_name)
        )
        return list(self.session.execute(stmt).all())

    def get_artists(self, id_user: int) -> list[Row[tuple[Any]]]:
        stmt = (
            select(Artist.id, Artist.artist_name)
            .select_from(AppUserArtist)
            .join(Artist, Artist.id == AppUserArtist.id_artist)
            .where(AppUserArtist.id_user == id_user)
            .order_by(Artist.artist_name)
        )
        return list(self.session.execute(stmt).all())

    def get_users(self, id_artist: int) -> list[Any]:
        users = list(
            self.session.scalars(
                select(AppUser)
                .join(AppUserArtist, AppUserArtist.id_user == AppUser.id)
                .where(AppUserArtist.id_artist == id_artist)
                .order_by(AppUser.lastfm_username)
            )
        )
        return users

    def save_all(self, all_artists: Sequence[dict], id_user: int) -> None:
        for artist_as_dict in all_artists:
            artist_name = artist_as_dict.get('artist_name')
            artist_url = artist_as_dict.get('artist_url')
            nb_scrobbles: int = artist_as_dict.get('nb_scrobbles', 0)

            # find or create artist
            existing_artist = self.session.scalar(
                select(Artist).where(Artist.artist_name == artist_name)
            )
            if existing_artist:
                artist = existing_artist
            else:
                artist = self.create(artist_name=artist_name, artist_url=artist_url)

            # create or update app_user_artist link
            link = self.session.get(AppUserArtist, (id_user, artist.id))
            if link:
                link.nb_scrobbles = nb_scrobbles or 0
            else:
                self.session.add(
                    AppUserArtist(
                        id_user=id_user,
                        id_artist=artist.id,
                        nb_scrobbles=nb_scrobbles,
                    )
                )
            self.session.flush()
            artist_as_dict['id'] = artist.id
