from datetime import date

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, Session

from db.database import get_session
from model.app_user_repository import AppUserRepository
from model.model import AppUserArtist, AppUser, AppUserSettings


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

def get_user_with_settings(user_id: int) -> tuple[AppUser, AppUserSettings | None]:
    with get_session() as session:
        stmt = (
            select(AppUser)
            .where(AppUser.id == user_id)
            .options(selectinload(AppUser.user_settings))
        )
        user = session.scalar(stmt)
        if not user:
            raise ValueError(f'User with id {user_id} not found')
        settings = user.user_settings
    return user, settings

def update_user_settings(user_id: int, min_scrobbles: int = None, releases_not_before: date = None) -> None:
    with get_session() as session:
        create_or_update_user_settings(session, user_id, min_scrobbles, releases_not_before)


def create_or_update_user_settings(session: Session,
                                   user_id: int,
                                   min_scrobbles: int | None = None,
                                   releases_not_before: date | None = None):
    stmt = select(AppUser).where(AppUser.id == user_id).options(selectinload(AppUser.user_settings))
    user = session.scalar(stmt)

    if user.user_settings:
        user.user_settings.min_scrobbles = min_scrobbles if min_scrobbles else user.user_settings.min_scrobbles
        user.user_settings.releases_not_before = releases_not_before if releases_not_before else user.user_settings.releases_not_before
    else:
        user.user_settings = AppUserSettings(
            id_user=user_id,
            min_scrobbles=min_scrobbles,
            releases_not_before=releases_not_before,
        )
    session.flush()


def create_user(lastfm_username: str):
    with get_session() as session:
        repo = AppUserRepository(session)
        existing_user = repo.get_by_lastfm_username(lastfm_username)
        if existing_user:
            create_or_update_user_settings(session, existing_user.id)
            return existing_user

        user = repo.create(lastfm_username=lastfm_username)
        session.flush()
        create_or_update_user_settings(session, user.id)
        return user

def delete_user(user_id: int):
    with get_session() as session:
        repo = AppUserRepository(session)
        repo.delete(user_id)

def update_user(new_username: str, user_id: int):
    with get_session() as session:
        repo = AppUserRepository(session)
        repo.update(user_id, username=new_username)
