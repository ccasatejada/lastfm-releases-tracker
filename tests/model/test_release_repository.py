from datetime import date

from model.artist_repository import ArtistRepository
from model.model import AppUser, AppUserRelease, Artist, Release
from model.release_repository import ReleaseRepository


def _add_artist(session, name='Radiohead') -> Artist:
    repo = ArtistRepository(session)
    artist = repo.create(artist_name=name)
    session.flush()
    return artist


def _add_release(
    session, artist_id: int, title='OK Computer', release_date=date(1997, 6, 16)
) -> Release:
    repo = ReleaseRepository(session)
    release = repo.create(
        release_title=title,
        release_date=release_date,
        length=3180,
        nb_tracks=12,
        id_artist=artist_id,
    )
    session.flush()
    return release


class TestGetAllWithArtist:
    def test_returns_empty_when_no_releases(self, in_memory_session):
        repo = ReleaseRepository(in_memory_session)
        assert repo.get_all_with_artist() == []

    def test_returns_release_with_artist_name(self, in_memory_session):
        artist = _add_artist(in_memory_session)
        release = _add_release(in_memory_session, artist.id)
        in_memory_session.commit()

        repo = ReleaseRepository(in_memory_session)
        rows = repo.get_all_with_artist()

        assert len(rows) == 1
        row = rows[0]
        assert row[0] == release.id
        assert row[1] == 'Radiohead'
        assert row[2] == 'OK Computer'
        assert row[3] == date(1997, 6, 16)

    def test_orders_by_date_descending(self, in_memory_session):
        artist = _add_artist(in_memory_session)
        _add_release(
            in_memory_session, artist.id, title='Old', release_date=date(1990, 1, 1)
        )
        _add_release(
            in_memory_session, artist.id, title='New', release_date=date(2023, 6, 1)
        )
        in_memory_session.commit()

        repo = ReleaseRepository(in_memory_session)
        rows = repo.get_all_with_artist()

        assert rows[0][2] == 'New'
        assert rows[1][2] == 'Old'

    def test_returns_releases_from_multiple_artists(self, in_memory_session):
        artist1 = _add_artist(in_memory_session, 'Radiohead')
        artist2 = _add_artist(in_memory_session, 'Muse')
        _add_release(in_memory_session, artist1.id, title='Kid A')
        _add_release(in_memory_session, artist2.id, title='Origin of Symmetry')
        in_memory_session.commit()

        repo = ReleaseRepository(in_memory_session)
        rows = repo.get_all_with_artist()

        titles = [r[2] for r in rows]
        assert 'Kid A' in titles
        assert 'Origin of Symmetry' in titles


class TestGetWithArtistAndUsers:
    def test_returns_release_and_artist(self, in_memory_session):
        artist = _add_artist(in_memory_session)
        release = _add_release(in_memory_session, artist.id)
        in_memory_session.commit()

        repo = ReleaseRepository(in_memory_session)
        result_release, result_artist, result_user_releases = (
            repo.get_with_artist_and_users(release.id)
        )

        assert result_release.release_title == 'OK Computer'
        assert result_artist.artist_name == 'Radiohead'
        assert result_user_releases == []

    def test_returns_user_releases_with_user(self, in_memory_session):
        artist = _add_artist(in_memory_session)
        release = _add_release(in_memory_session, artist.id)

        user = AppUser(lastfm_username='alice')
        in_memory_session.add(user)
        in_memory_session.flush()

        user_release = AppUserRelease(
            id_user=user.id, id_release=release.id, ignored=False
        )
        in_memory_session.add(user_release)
        in_memory_session.commit()

        repo = ReleaseRepository(in_memory_session)
        _, _, result_user_releases = repo.get_with_artist_and_users(release.id)

        assert len(result_user_releases) == 1
        assert result_user_releases[0].user.lastfm_username == 'alice'
        assert result_user_releases[0].ignored is False

    def test_returns_multiple_user_releases(self, in_memory_session):
        artist = _add_artist(in_memory_session)
        release = _add_release(in_memory_session, artist.id)

        for username in ('alice', 'bob'):
            user = AppUser(lastfm_username=username)
            in_memory_session.add(user)
            in_memory_session.flush()
            in_memory_session.add(
                AppUserRelease(id_user=user.id, id_release=release.id)
            )

        in_memory_session.commit()

        repo = ReleaseRepository(in_memory_session)
        _, _, result_user_releases = repo.get_with_artist_and_users(release.id)

        usernames = {ur.user.lastfm_username for ur in result_user_releases}
        assert usernames == {'alice', 'bob'}
