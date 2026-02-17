from unittest.mock import patch

from service import default_user_service


class TestGetDefaultUser:
    @patch.dict(
        'os.environ', {'LASTFM_USERNAME': 'myuser', 'LASTFM_PASSWORD': 'mypass'}
    )
    def test_returns_env_values(self):
        password, username = default_user_service.get_default_user()
        assert username == 'myuser'
        assert password == 'mypass'

    @patch.dict('os.environ', {}, clear=True)
    def test_returns_none_when_not_set(self):
        password, username = default_user_service.get_default_user()
        assert username is None
        assert password is None

    @patch.dict('os.environ', {'LASTFM_USERNAME': 'onlyuser'}, clear=True)
    def test_returns_none_password_when_only_username(self):
        password, username = default_user_service.get_default_user()
        assert username == 'onlyuser'
        assert password is None
