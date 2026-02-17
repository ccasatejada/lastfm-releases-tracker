from datetime import date
from unittest.mock import MagicMock, patch

from model.model import AppUser, AppUserArtist, Artist, Release
from service import artist_service


class TestSaveArtists:
    def test_creates_new_artist_and_link(self, mock_get_session):
        artists_data = [
            {
                'artist_name': 'Radiohead',
                'artist_url': 'https://last.fm/music/Radiohead',
                'nb_scrobbles': 5000,
            }
        ]
        new_artist = Artist(id=1, artist_name='Radiohead')
        repo_mock = MagicMock()
        repo_mock.create.return_value = new_artist

        with patch('service.artist_service.get_session', mock_get_session):
            with mock_get_session() as session:
                session.scalar.return_value = None  # no existing artist
                session.get.return_value = None  # no existing link

            with patch('service.artist_service.get_session', mock_get_session):
                with patch(
                    'service.artist_service.ArtistRepository', return_value=repo_mock
                ):
                    artist_service.save_artists(artists_data, id_user=1)

        repo_mock.create.assert_called_once_with(
            artist_name='Radiohead',
            artist_url='https://last.fm/music/Radiohead',
        )
        assert artists_data[0]['id'] == 1

    def test_updates_existing_artist_link(self, mock_get_session):
        artists_data = [
            {
                'artist_name': 'Radiohead',
                'artist_url': 'https://last.fm/music/Radiohead',
                'nb_scrobbles': 8000,
            }
        ]
        existing_artist = Artist(id=1, artist_name='Radiohead')
        existing_link = AppUserArtist(id_user=1, id_artist=1, nb_scrobbles=5000)

        with patch('service.artist_service.get_session', mock_get_session):
            with mock_get_session() as session:
                session.scalar.return_value = existing_artist
                session.get.return_value = existing_link

            with patch('service.artist_service.get_session', mock_get_session):
                with patch('service.artist_service.ArtistRepository'):
                    artist_service.save_artists(artists_data, id_user=1)

        assert existing_link.nb_scrobbles == 8000

    def test_saves_multiple_artists(self, mock_get_session):
        artists_data = [
            {'artist_name': 'Artist1', 'artist_url': 'url1', 'nb_scrobbles': 100},
            {'artist_name': 'Artist2', 'artist_url': 'url2', 'nb_scrobbles': 200},
        ]
        repo_mock = MagicMock()
        repo_mock.create.side_effect = [
            Artist(id=1, artist_name='Artist1'),
            Artist(id=2, artist_name='Artist2'),
        ]

        with patch('service.artist_service.get_session', mock_get_session):
            with mock_get_session() as session:
                session.scalar.return_value = None
                session.get.return_value = None

            with patch('service.artist_service.get_session', mock_get_session):
                with patch(
                    'service.artist_service.ArtistRepository', return_value=repo_mock
                ):
                    artist_service.save_artists(artists_data, id_user=1)

        assert repo_mock.create.call_count == 2
        assert artists_data[0]['id'] == 1
        assert artists_data[1]['id'] == 2


class TestGetArtist:
    def test_returns_artist(self, mock_get_session):
        artist = Artist(id=1, artist_name='Radiohead')

        with patch('service.artist_service.get_session', mock_get_session):
            with mock_get_session() as session:
                session.scalar.return_value = artist

            with patch('service.artist_service.get_session', mock_get_session):
                result = artist_service.get_artist(1)

        assert result.artist_name == 'Radiohead'

    def test_returns_none_when_not_found(self, mock_get_session):
        with patch('service.artist_service.get_session', mock_get_session):
            with mock_get_session() as session:
                session.scalar.return_value = None

            with patch('service.artist_service.get_session', mock_get_session):
                result = artist_service.get_artist(999)

        assert result is None


class TestGetAllArtistsWithCounts:
    def test_returns_list(self, mock_get_session):
        rows = [
            (1, 'Radiohead', 5, 2, None, None),
            (2, 'Muse', 3, 1, None, None),
        ]

        with patch('service.artist_service.get_session', mock_get_session):
            with mock_get_session() as session:
                session.execute.return_value.all.return_value = rows

            with patch('service.artist_service.get_session', mock_get_session):
                result = artist_service.get_all_artists_with_counts()

        assert len(result) == 2
        assert result[0][1] == 'Radiohead'


class TestGetArtistDetail:
    def test_returns_artist_users_releases(self, mock_get_session):
        release1 = Release(
            id=1,
            release_title='OK Computer',
            release_date=date(1997, 6, 16),
            length=53,
            nb_tracks=12,
            id_artist=1,
        )
        release2 = Release(
            id=2,
            release_title='Kid A',
            release_date=date(2000, 10, 2),
            length=49,
            nb_tracks=10,
            id_artist=1,
        )
        artist = Artist(id=1, artist_name='Radiohead')
        artist.releases = [release1, release2]
        user = AppUser(id=1, lastfm_username='alice')

        with patch('service.artist_service.get_session', mock_get_session):
            with mock_get_session() as session:
                session.scalar.return_value = artist
                session.scalars.return_value = [user]

            with patch('service.artist_service.get_session', mock_get_session):
                result_artist, result_users, result_releases = (
                    artist_service.get_artist_detail(1)
                )

        assert result_artist.artist_name == 'Radiohead'
        assert len(result_users) == 1
        assert len(result_releases) == 2
        # releases should be sorted by date descending
        assert result_releases[0].release_title == 'Kid A'
