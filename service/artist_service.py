from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from db.database import get_session
from model.artist_repository import ArtistRepository
from model.model import Artist, AppUser, AppUserArtist, Release


def save_artists(all_artists, user_id):
    with get_session() as session:
        repo = ArtistRepository(session)

        for artist_as_dict in all_artists:
            artist_name = artist_as_dict.get('artist_name')
            artist_url = artist_as_dict.get('artist_url')
            nb_scrobbles = artist_as_dict.get('nb_scrobbles')

            # find or create artist
            existing_artist = session.scalar(
                select(Artist).where(Artist.artist_name == artist_name)
            )
            if existing_artist:
                artist = existing_artist
            else:
                artist = repo.create(artist_name=artist_name, artist_url=artist_url)

            # create or update app_user_artist link
            link = session.get(AppUserArtist, (user_id, artist.id))
            if link:
                link.nb_scrobbles = nb_scrobbles
            else:
                session.add(AppUserArtist(
                    id_user=user_id,
                    id_artist=artist.id,
                    nb_scrobbles=nb_scrobbles,
                ))
            session.flush()

            artist_as_dict['id'] = artist.id


def get_all_artists_with_counts():
    """Returns list of (id, artist_name, nb_releases, nb_users, created_at, updated_at)."""
    with get_session() as session:
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
            .group_by(Artist.id, Artist.artist_name, Artist.created_at, Artist.updated_at)
            .order_by(Artist.artist_name)
        )
        return list(session.execute(stmt).all())


def get_artist_detail(artist_id: int) -> tuple[Artist, list[AppUser], list[Release]]:
    """Returns (artist, users, releases) for the given artist."""
    with get_session() as session:
        artist = session.scalar(
            select(Artist)
            .where(Artist.id == artist_id)
            .options(selectinload(Artist.releases))
        )

        users = list(session.scalars(
            select(AppUser)
            .join(AppUserArtist, AppUserArtist.id_user == AppUser.id)
            .where(AppUserArtist.id_artist == artist_id)
            .order_by(AppUser.lastfm_username)
        ))

        releases = sorted(artist.releases, key=lambda r: r.release_date, reverse=True)

        return artist, users, releases
