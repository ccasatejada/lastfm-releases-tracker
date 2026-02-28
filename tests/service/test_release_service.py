from datetime import date
from unittest.mock import patch

from model.model import AppUser, AppUserRelease, Artist, Release
from model.release_repository import ReleaseRepository
from service import release_service


class TestSaveReleases:
    def test_creates_new_release_and_link(self, mock_get_session):
        releases_data = [
            {
                'release_title': 'OK Computer',
                'release_date': date(1997, 6, 16),
                'length': 53,
                'nb_tracks': 12,
                'release_url': 'https://last.fm/music/Radiohead/OK+Computer',
            }
        ]
        new_release = Release(
            id=1,
            release_title='OK Computer',
            release_date=date(1997, 6, 16),
            length=53,
            nb_tracks=12,
            id_artist=1,
        )

        with mock_get_session() as session:
            session.scalars.return_value.one_or_none.return_value = (
                None  # no existing release
            )
            session.get.return_value = None  # no existing link

        with patch('service.release_service.get_session', mock_get_session):
            with patch.object(
                ReleaseRepository, 'create', return_value=new_release
            ) as mock_create:
                release_service.save_releases(releases_data, id_artist=1, id_user=1)

        mock_create.assert_called_once()
        assert releases_data[0]['id'] == 1

    def test_updates_existing_release(self, mock_get_session):
        releases_data = [
            {
                'release_title': 'OK Computer',
                'release_date': date(1997, 6, 16),
                'length': 53,
                'nb_tracks': 12,
                'release_url': 'https://last.fm/music/Radiohead/OK+Computer',
            }
        ]
        existing_release = Release(
            id=1,
            release_title='OK Computer',
            release_date=date(1990, 1, 1),
            length=0,
            nb_tracks=0,
            id_artist=1,
        )
        existing_link = AppUserRelease(id_user=1, id_release=1)

        with mock_get_session() as session:
            session.scalars.return_value.one_or_none.return_value = existing_release
            session.get.return_value = existing_link

        with patch('service.release_service.get_session', mock_get_session):
            release_service.save_releases(releases_data, id_artist=1, id_user=1)

        assert existing_release.release_date == date(1997, 6, 16)
        assert existing_release.nb_tracks == 12
        assert existing_release.length == 53
        assert releases_data[0]['id'] == 1

    def test_creates_link_when_missing(self, mock_get_session):
        releases_data = [
            {
                'release_title': 'OK Computer',
                'release_date': date(1997, 6, 16),
                'length': 53,
                'nb_tracks': 12,
                'release_url': 'url',
            }
        ]
        existing_release = Release(
            id=1,
            release_title='OK Computer',
            release_date=date(1997, 6, 16),
            length=53,
            nb_tracks=12,
            id_artist=1,
        )

        with mock_get_session() as session:
            session.scalars.return_value.one_or_none.return_value = existing_release
            session.get.return_value = None  # no link

        with patch('service.release_service.get_session', mock_get_session):
            release_service.save_releases(releases_data, id_artist=1, id_user=1)

        # verify session.add was called for the link
        with mock_get_session() as session:
            session.add.assert_called()

    def test_saves_multiple_releases(self, mock_get_session):
        releases_data = [
            {
                'release_title': 'Album1',
                'release_date': date(2020, 1, 1),
                'length': 40,
                'nb_tracks': 10,
                'release_url': 'u1',
            },
            {
                'release_title': 'Album2',
                'release_date': date(2021, 1, 1),
                'length': 45,
                'nb_tracks': 11,
                'release_url': 'u2',
            },
        ]

        with mock_get_session() as session:
            session.scalars.return_value.one_or_none.return_value = None
            session.get.return_value = None

        with patch('service.release_service.get_session', mock_get_session):
            with patch.object(
                ReleaseRepository,
                'create',
                side_effect=[
                    Release(
                        id=1,
                        release_title='Album1',
                        release_date=date(2020, 1, 1),
                        length=40,
                        nb_tracks=10,
                        id_artist=1,
                    ),
                    Release(
                        id=2,
                        release_title='Album2',
                        release_date=date(2021, 1, 1),
                        length=45,
                        nb_tracks=11,
                        id_artist=1,
                    ),
                ],
            ) as mock_create:
                release_service.save_releases(releases_data, id_artist=1, id_user=1)

        assert mock_create.call_count == 2
        assert releases_data[0]['id'] == 1
        assert releases_data[1]['id'] == 2


class TestGetAllReleases:
    def test_returns_list_of_rows(self, mock_get_session):
        rows = [
            (
                1,
                'Radiohead',
                'OK Computer',
                date(1997, 6, 16),
                3180,
                12,
                'https://example.com',
            ),
            (2, 'Muse', 'Origin of Symmetry', date(2001, 6, 11), 2940, 11, None),
        ]

        with patch('service.release_service.get_session', mock_get_session):
            with mock_get_session() as session:
                session.execute.return_value.all.return_value = rows

            with patch('service.release_service.get_session', mock_get_session):
                result = release_service.get_all_releases()

        assert len(result) == 2
        assert result[0][1] == 'Radiohead'
        assert result[1][2] == 'Origin of Symmetry'

    def test_returns_empty_list_when_no_releases(self, mock_get_session):
        with patch('service.release_service.get_session', mock_get_session):
            with mock_get_session() as session:
                session.execute.return_value.all.return_value = []

            with patch('service.release_service.get_session', mock_get_session):
                result = release_service.get_all_releases()

        assert result == []


class TestGetReleaseDetail:
    def test_returns_release_artist_and_user_releases(self, mock_get_session):
        artist = Artist(id=1, artist_name='Radiohead')
        release = Release(
            id=1,
            release_title='OK Computer',
            release_date=date(1997, 6, 16),
            length=3180,
            nb_tracks=12,
            id_artist=1,
        )
        release.artist = artist
        release.user_releases = []

        with mock_get_session() as session:
            session.scalar.return_value = release

        with patch('service.release_service.get_session', mock_get_session):
            result_release, result_artist, result_user_releases = (
                release_service.get_release_detail(1)
            )

        assert result_release.release_title == 'OK Computer'
        assert result_artist.artist_name == 'Radiohead'
        assert result_user_releases == []

    def test_returns_user_releases_with_user_info(self, mock_get_session):
        artist = Artist(id=1, artist_name='Radiohead')
        release = Release(
            id=1,
            release_title='OK Computer',
            release_date=date(1997, 6, 16),
            length=3180,
            nb_tracks=12,
            id_artist=1,
        )
        user = AppUser(id=1, lastfm_username='alice')
        ur = AppUserRelease(id_user=1, id_release=1, ignored=True)
        ur.user = user
        release.artist = artist
        release.user_releases = [ur]

        with mock_get_session() as session:
            session.scalar.return_value = release

        with patch('service.release_service.get_session', mock_get_session):
            _, _, result_user_releases = release_service.get_release_detail(1)

        assert len(result_user_releases) == 1
        assert result_user_releases[0].user.lastfm_username == 'alice'
        assert result_user_releases[0].ignored is True
