from datetime import date
from unittest.mock import patch

from model.model import AppUserRelease, Release
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
