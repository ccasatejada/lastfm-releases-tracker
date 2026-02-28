from unittest.mock import MagicMock, patch

import pytest
from requests import HTTPError

from scrapper.internal.login import create_lastfm_session


def _make_session_mock(csrf='token123', redirect_url='/fr/user/_'):
    session = MagicMock()

    get_resp = MagicMock()
    get_resp.text = f'<input name="csrfmiddlewaretoken" value="{csrf}"/>'
    session.get.return_value = get_resp

    post_resp = MagicMock()
    post_resp.url = redirect_url
    post_resp.raise_for_status = MagicMock()
    session.post.return_value = post_resp

    return session


class TestCreateLastfmSession:
    def test_returns_session_on_success(self):
        mock_session = _make_session_mock()
        with patch(
            'scrapper.internal.login.requests.Session', return_value=mock_session
        ):
            result = create_lastfm_session('alice', 'pass123')
        assert result is mock_session

    def test_raises_value_error_on_login_redirect(self):
        mock_session = _make_session_mock(
            redirect_url='https://www.last.fm/login?next=...'
        )
        with patch(
            'scrapper.internal.login.requests.Session', return_value=mock_session
        ):
            with pytest.raises(ValueError, match='login failed'):
                create_lastfm_session('alice', 'wrongpass')

    def test_raises_on_http_error(self):
        mock_session = _make_session_mock()
        mock_session.post.return_value.raise_for_status.side_effect = HTTPError('403')
        with patch(
            'scrapper.internal.login.requests.Session', return_value=mock_session
        ):
            with pytest.raises(HTTPError):
                create_lastfm_session('alice', 'pass')

    def test_posts_correct_credentials(self):
        mock_session = _make_session_mock(csrf='mytoken')
        with patch(
            'scrapper.internal.login.requests.Session', return_value=mock_session
        ):
            create_lastfm_session('alice', 'pass123')
        data = mock_session.post.call_args.kwargs['data']
        assert data['username_or_email'] == 'alice'
        assert data['password'] == 'pass123'
        assert data['csrfmiddlewaretoken'] == 'mytoken'
