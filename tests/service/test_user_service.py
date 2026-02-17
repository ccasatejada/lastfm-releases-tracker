from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from model.model import AppUser, AppUserSettings
from service import user_service


class TestGetUser:
    def test_returns_user(self, mock_get_session):
        user = AppUser(id=1, lastfm_username='alice')
        repo_mock = MagicMock()
        repo_mock.get_by_lastfm_username.return_value = user

        with patch('service.user_service.get_session', mock_get_session):
            with patch(
                'service.user_service.AppUserRepository', return_value=repo_mock
            ):
                result = user_service.get_user('alice')

        assert result.lastfm_username == 'alice'
        repo_mock.get_by_lastfm_username.assert_called_once_with('alice')

    def test_raises_when_user_not_found(self, mock_get_session):
        repo_mock = MagicMock()
        repo_mock.get_by_lastfm_username.return_value = None

        with patch('service.user_service.get_session', mock_get_session):
            with patch(
                'service.user_service.AppUserRepository', return_value=repo_mock
            ):
                with pytest.raises(ValueError, match='not found'):
                    user_service.get_user('unknown')


class TestGetUsers:
    def test_returns_counts_and_users(self, mock_get_session):
        repo_mock = MagicMock()
        repo_mock.get_all.return_value = [
            AppUser(id=1, lastfm_username='alice'),
            AppUser(id=2, lastfm_username='bob'),
        ]

        with mock_get_session() as session:
            session.execute.return_value.all.return_value = [(1, 5), (2, 3)]

        with patch('service.user_service.get_session', mock_get_session):
            with patch(
                'service.user_service.AppUserRepository', return_value=repo_mock
            ):
                counts, users = user_service.get_users()

        assert len(users) == 2


class TestGetUserWithSettings:
    def test_returns_user_and_settings(self, mock_get_session):
        settings = AppUserSettings(id=1, id_user=1, min_scrobbles=500)
        user = AppUser(id=1, lastfm_username='alice')
        user.user_settings = settings

        with mock_get_session() as session:
            session.scalar.return_value = user

        with patch('service.user_service.get_session', mock_get_session):
            result_user, result_settings = user_service.get_user_with_settings(1)

        assert result_user.lastfm_username == 'alice'
        assert result_settings.min_scrobbles == 500

    def test_raises_when_user_not_found(self, mock_get_session):
        with mock_get_session() as session:
            session.scalar.return_value = None

        with patch('service.user_service.get_session', mock_get_session):
            with pytest.raises(ValueError, match='not found'):
                user_service.get_user_with_settings(999)


class TestCreateUser:
    def test_creates_new_user(self, mock_get_session):
        new_user = AppUser(id=1, lastfm_username='alice')
        new_user.user_settings = None

        repo_mock = MagicMock()
        repo_mock.get_by_lastfm_username.return_value = None
        repo_mock.create.return_value = new_user

        with mock_get_session() as session:
            user_with_settings = AppUser(id=1, lastfm_username='alice')
            user_with_settings.user_settings = None
            session.scalar.return_value = user_with_settings

        with patch('service.user_service.get_session', mock_get_session):
            with patch(
                'service.user_service.AppUserRepository', return_value=repo_mock
            ):
                result = user_service.create_user('alice')

        assert result.lastfm_username == 'alice'

    def test_returns_existing_user(self, mock_get_session):
        existing = AppUser(id=1, lastfm_username='alice')
        existing.user_settings = AppUserSettings(id=1, id_user=1, min_scrobbles=1000)

        repo_mock = MagicMock()
        repo_mock.get_by_lastfm_username.return_value = existing

        with mock_get_session() as session:
            session.scalar.return_value = existing

        with patch('service.user_service.get_session', mock_get_session):
            with patch(
                'service.user_service.AppUserRepository', return_value=repo_mock
            ):
                result = user_service.create_user('alice')

        assert result.id == 1


class TestDeleteUser:
    def test_delete_calls_repo(self, mock_get_session):
        repo_mock = MagicMock()

        with patch('service.user_service.get_session', mock_get_session):
            with patch(
                'service.user_service.AppUserRepository', return_value=repo_mock
            ):
                user_service.delete_user(1)

        repo_mock.delete.assert_called_once_with(1)


class TestUpdateUser:
    def test_update_calls_repo(self, mock_get_session):
        repo_mock = MagicMock()

        with patch('service.user_service.get_session', mock_get_session):
            with patch(
                'service.user_service.AppUserRepository', return_value=repo_mock
            ):
                user_service.update_user('new_name', 1)

        repo_mock.update.assert_called_once_with(1, username='new_name')


class TestUpdateUserSettings:
    def test_updates_existing_settings(self, mock_get_session):
        settings = AppUserSettings(id=1, id_user=1, min_scrobbles=500)
        user = AppUser(id=1, lastfm_username='alice')
        user.user_settings = settings

        with mock_get_session() as session:
            session.scalar.return_value = user

        with patch('service.user_service.get_session', mock_get_session):
            user_service.update_user_settings(1, min_scrobbles=2000)

        assert user.user_settings.min_scrobbles == 2000

    def test_creates_settings_when_none(self, mock_get_session):
        user = AppUser(id=1, lastfm_username='alice')
        user.user_settings = None

        with mock_get_session() as session:
            session.scalar.return_value = user

        with patch('service.user_service.get_session', mock_get_session):
            user_service.update_user_settings(
                1, min_scrobbles=800, releases_not_before=date(2023, 1, 1)
            )

        assert user.user_settings is not None
        assert user.user_settings.min_scrobbles == 800
