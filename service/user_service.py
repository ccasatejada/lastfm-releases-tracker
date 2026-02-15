from sqlalchemy import select, func

from db.database import get_session
from model.app_user_repository import AppUserRepository
from model.model import AppUserArtist, AppUser


def get_users():
    with get_session() as session:
        repo = AppUserRepository(session)
        users = repo.get_all()

        counts = dict(
            session.execute(
                select(AppUserArtist.id_user, func.count())
                .group_by(AppUserArtist.id_user)
            ).all()
        )
    return counts, users

def get_user(lastfm_username: str) -> AppUser:
    with get_session() as session:
        repo = AppUserRepository(session)
        user = repo.get_by_lastfm_username(lastfm_username)
        if not user:
            raise ValueError(f'User "{lastfm_username}" not found in database')
    return user

def delete_user(user_id: int):
    with get_session() as session:
        repo = AppUserRepository(session)
        repo.delete(user_id)

def update_user(new_username: str, user_id: int):
    with get_session() as session:
        repo = AppUserRepository(session)
        repo.update(user_id, username=new_username)
