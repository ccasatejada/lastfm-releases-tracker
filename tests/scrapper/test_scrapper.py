from unittest.mock import MagicMock, patch

import pytest
import requests

from model.model import AppUser
from scrapper import scrapper


class TestInitUser:
    @patch('scrapper.scrapper.user_service')
    @patch('scrapper.scrapper.requests.get')
    def test_creates_user_when_exists_on_lastfm(self, mock_get, mock_user_svc):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        expected_user = AppUser(id=1, lastfm_username='alice')
        mock_user_svc.create_user.return_value = expected_user

        result = scrapper.init_user('alice')

        assert result.lastfm_username == 'alice'
        mock_user_svc.create_user.assert_called_once_with('alice')

    @patch('scrapper.scrapper.requests.get')
    def test_raises_when_user_not_found_on_lastfm(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match='does not exist'):
            scrapper.init_user('nonexistent_user')

    @patch('scrapper.scrapper.requests.get')
    def test_raises_on_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError('Server Error')
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            scrapper.init_user('alice')


class TestFetchArtists:
    @patch('scrapper.scrapper.ArtistsFetcher')
    def test_creates_fetcher_and_calls_fetch(self, mock_fetcher_cls):
        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        callback = MagicMock()

        scrapper.fetch_artists('user', 'pass', callback)

        mock_fetcher_cls.assert_called_once_with('user', 'pass')
        mock_fetcher.fetch.assert_called_once_with(callback)

    @patch('scrapper.scrapper.ArtistsFetcher')
    def test_works_without_callback(self, mock_fetcher_cls):
        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher

        scrapper.fetch_artists('user', 'pass')

        mock_fetcher.fetch.assert_called_once_with(None)


class TestFetchReleases:
    @patch('scrapper.scrapper.ReleasesFetcher')
    def test_creates_fetcher_and_calls_fetch(self, mock_fetcher_cls):
        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        callback = MagicMock()

        scrapper.fetch_releases('user', 'pass', 42, callback)

        mock_fetcher_cls.assert_called_once_with('user', 'pass', 42, None)
        mock_fetcher.fetch.assert_called_once_with(callback)

    @patch('scrapper.scrapper.ReleasesFetcher')
    def test_passes_http_session(self, mock_fetcher_cls):
        mock_fetcher = MagicMock()
        mock_fetcher_cls.return_value = mock_fetcher
        http_session = MagicMock(spec=requests.Session)

        scrapper.fetch_releases('user', 'pass', 42, http_session=http_session)

        mock_fetcher_cls.assert_called_once_with('user', 'pass', 42, http_session)


class TestFetchAllReleases:
    @patch('scrapper.scrapper.fetch_releases')
    @patch('scrapper.scrapper.BaseFetcher')
    @patch('scrapper.scrapper.user_service')
    def test_fetches_releases_for_all_user_artists(
        self, mock_user_svc, mock_base_fetcher_cls, mock_fetch_releases
    ):
        user = AppUser(id=1, lastfm_username='alice')
        mock_user_svc.get_user.return_value = user

        mock_user_svc.get_user_artists.return_value = [(10, 'Artist1'), (20, 'Artist2')]

        mock_base = MagicMock()
        mock_session = MagicMock()
        mock_base.get_http_session.return_value = mock_session
        mock_base_fetcher_cls.return_value = mock_base

        callback = MagicMock()
        scrapper.fetch_all_releases('alice', 'pass', callback)

        assert mock_fetch_releases.call_count == 2
        mock_fetch_releases.assert_any_call('alice', 'pass', 10, callback, mock_session)
        mock_fetch_releases.assert_any_call('alice', 'pass', 20, callback, mock_session)
