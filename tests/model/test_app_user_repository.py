from datetime import date

import pytest

from model.app_user_repository import AppUserRepository
from model.model import AppUserSettings


class TestGetByLastfmUsername:
    def test_returns_user_when_found(self, in_memory_session):
        repo = AppUserRepository(in_memory_session)
        repo.create(lastfm_username='alice')
        in_memory_session.commit()
        user = repo.get_by_lastfm_username('alice')
        assert user is not None
        assert user.lastfm_username == 'alice'

    def test_returns_none_when_missing(self, in_memory_session):
        repo = AppUserRepository(in_memory_session)
        assert repo.get_by_lastfm_username('nobody') is None


class TestGetUsers:
    def test_returns_all_users(self, in_memory_session):
        repo = AppUserRepository(in_memory_session)
        repo.create(lastfm_username='alice')
        repo.create(lastfm_username='bob')
        in_memory_session.commit()
        counts, users = repo.get_users()
        assert len(users) == 2

    def test_counts_empty_when_no_artists(self, in_memory_session):
        repo = AppUserRepository(in_memory_session)
        repo.create(lastfm_username='alice')
        in_memory_session.commit()
        counts, _ = repo.get_users()
        assert counts == {}


class TestGetUserWithSettings:
    def test_returns_user_and_settings(self, in_memory_session):
        repo = AppUserRepository(in_memory_session)
        user = repo.create(lastfm_username='alice')
        in_memory_session.flush()
        settings = AppUserSettings(id_user=user.id)
        in_memory_session.add(settings)
        in_memory_session.commit()
        result_user, result_settings = repo.get_user_with_settings(user.id)
        assert result_user.lastfm_username == 'alice'
        assert result_settings is not None

    def test_raises_when_user_not_found(self, in_memory_session):
        repo = AppUserRepository(in_memory_session)
        with pytest.raises(ValueError, match='not found'):
            repo.get_user_with_settings(9999)


class TestCreateUser:
    def test_creates_new_user_with_settings(self, in_memory_session):
        repo = AppUserRepository(in_memory_session)
        user = repo.create_user('newuser')
        in_memory_session.commit()
        assert user.lastfm_username == 'newuser'
        assert user.id is not None

    def test_returns_existing_user_when_already_exists(self, in_memory_session):
        repo = AppUserRepository(in_memory_session)
        user1 = repo.create_user('alice')
        in_memory_session.commit()
        user2 = repo.create_user('alice')
        assert user1.id == user2.id


class TestCreateOrUpdateUserSettings:
    def test_creates_settings_when_none_exist(self, in_memory_session):
        repo = AppUserRepository(in_memory_session)
        user = repo.create(lastfm_username='alice')
        in_memory_session.flush()
        repo.create_or_update_user_settings(user.id, min_scrobbles=500)
        in_memory_session.commit()
        _, settings = repo.get_user_with_settings(user.id)
        assert settings.min_scrobbles == 500

    def test_updates_existing_settings(self, in_memory_session):
        repo = AppUserRepository(in_memory_session)
        user = repo.create_user('alice')
        in_memory_session.commit()
        repo.create_or_update_user_settings(user.id, min_scrobbles=2000)
        in_memory_session.commit()
        _, settings = repo.get_user_with_settings(user.id)
        assert settings.min_scrobbles == 2000

    def test_updates_releases_not_before(self, in_memory_session):
        repo = AppUserRepository(in_memory_session)
        user = repo.create_user('alice')
        in_memory_session.commit()
        repo.create_or_update_user_settings(
            user.id, releases_not_before=date(2022, 6, 1)
        )
        in_memory_session.commit()
        _, settings = repo.get_user_with_settings(user.id)
        assert settings.releases_not_before == date(2022, 6, 1)
