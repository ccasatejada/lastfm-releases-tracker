from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from db.database import get_session
from model.app_user_repository import AppUserRepository
from model.model import AppUser, AppUserArtist, AppUserSettings, Artist


def get_users() -> tuple[
    dict[Any, Any] | dict[str, Any] | dict[str, str] | dict[bytes, bytes], list[AppUser]
]:
    with get_session() as session:
        repo = AppUserRepository(session)
        users = repo.get_all()

        counts = dict(
            session.execute(
                select(AppUserArtist.id_user, func.count()).group_by(
                    AppUserArtist.id_user
                )
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


def get_user_with_settings(id_user: int) -> tuple[AppUser, AppUserSettings | None]:
    with get_session() as session:
        stmt = (
            select(AppUser)
            .where(AppUser.id == id_user)
            .options(selectinload(AppUser.user_settings))
        )
        user = session.scalar(stmt)
        if not user:
            raise ValueError(f'User with id {id_user} not found')
        settings = user.user_settings
    return user, settings


def update_user_settings(
    id_user: int, min_scrobbles: int = None, releases_not_before: date = None
) -> None:
    with get_session() as session:
        create_or_update_user_settings(
            session, id_user, min_scrobbles, releases_not_before
        )


def create_or_update_user_settings(
    session: Session,
    id_user: int,
    min_scrobbles: int | None = None,
    releases_not_before: date | None = None,
) -> None:
    stmt = (
        select(AppUser)
        .where(AppUser.id == id_user)
        .options(selectinload(AppUser.user_settings))
    )
    user: AppUser = session.scalar(stmt)  # type: ignore[assignment]

    if user.user_settings:
        user.user_settings.min_scrobbles = (
            min_scrobbles if min_scrobbles else user.user_settings.min_scrobbles
        )
        user.user_settings.releases_not_before = (
            releases_not_before
            if releases_not_before
            else user.user_settings.releases_not_before
        )
    else:
        user.user_settings = AppUserSettings(
            id_user=id_user,
            min_scrobbles=min_scrobbles,
            releases_not_before=releases_not_before,
        )
    session.flush()


def create_user(lastfm_username: str) -> AppUser:
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


def get_user_artists(id_user: int) -> list[tuple[int, str]]:
    with get_session() as session:
        stmt = (
            select(Artist.id, Artist.artist_name)
            .select_from(AppUserArtist)
            .join(Artist, Artist.id == AppUserArtist.id_artist)
            .where(AppUserArtist.id_user == id_user)
            .order_by(Artist.artist_name)
        )
        return list(session.execute(stmt).all())


def delete_user(id_user: int) -> None:
    with get_session() as session:
        repo = AppUserRepository(session)
        repo.delete(id_user)


def update_user(new_username: str, id_user: int) -> None:
    with get_session() as session:
        repo = AppUserRepository(session)
        repo.update(id_user, username=new_username)
