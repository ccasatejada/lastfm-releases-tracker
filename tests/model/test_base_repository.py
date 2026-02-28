from model.internal.base_repository import BaseRepository
from model.model import AppUser


class TestBaseRepository:
    def test_create_adds_and_returns_instance(self, in_memory_session):
        repo = BaseRepository(in_memory_session, AppUser)
        user = repo.create(lastfm_username='alice')
        assert user.lastfm_username == 'alice'
        assert user.id is not None

    def test_get_returns_existing_instance(self, in_memory_session):
        repo = BaseRepository(in_memory_session, AppUser)
        user = repo.create(lastfm_username='alice')
        in_memory_session.commit()
        found = repo.get(user.id)
        assert found is not None
        assert found.lastfm_username == 'alice'

    def test_get_returns_none_for_missing_id(self, in_memory_session):
        repo = BaseRepository(in_memory_session, AppUser)
        assert repo.get(9999) is None

    def test_get_all_returns_all_instances(self, in_memory_session):
        repo = BaseRepository(in_memory_session, AppUser)
        repo.create(lastfm_username='alice')
        repo.create(lastfm_username='bob')
        in_memory_session.commit()
        results = repo.get_all()
        assert len(results) == 2

    def test_get_all_respects_limit(self, in_memory_session):
        repo = BaseRepository(in_memory_session, AppUser)
        for i in range(5):
            repo.create(lastfm_username=f'user{i}')
        in_memory_session.commit()
        results = repo.get_all(limit=2)
        assert len(results) == 2

    def test_update_modifies_field(self, in_memory_session):
        repo = BaseRepository(in_memory_session, AppUser)
        user = repo.create(lastfm_username='alice')
        in_memory_session.commit()
        updated = repo.update(user.id, username='Alice Updated')
        assert updated is not None
        assert updated.username == 'Alice Updated'

    def test_update_returns_none_for_missing_id(self, in_memory_session):
        repo = BaseRepository(in_memory_session, AppUser)
        result = repo.update(9999, username='Ghost')
        assert result is None

    def test_delete_removes_instance_and_returns_true(self, in_memory_session):
        repo = BaseRepository(in_memory_session, AppUser)
        user = repo.create(lastfm_username='alice')
        in_memory_session.commit()
        result = repo.delete(user.id)
        assert result is True
        assert repo.get(user.id) is None

    def test_delete_returns_false_for_missing_id(self, in_memory_session):
        repo = BaseRepository(in_memory_session, AppUser)
        result = repo.delete(9999)
        assert result is False
