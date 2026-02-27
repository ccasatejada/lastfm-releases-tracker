from datetime import date
from typing import Any

from sqlalchemy import Row

from db.database import get_session
from model.app_user_repository import AppUserRepository
from model.artist_repository import ArtistRepository
from model.model import AppUser, AppUserSettings


def get_users() -> tuple[
    dict[Any, Any] | dict[str, Any] | dict[str, str] | dict[bytes, bytes], list[AppUser]
]:
    with get_session() as session:
        repo = AppUserRepository(session)
        counts, users = repo.get_users()
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
        repo = AppUserRepository(session)
        try:
            user, settings = repo.get_user_with_settings(id_user)
        except ValueError as e:
            raise e
    return user, settings


def update_user_settings(
    id_user: int,
    username: str = None,
    min_scrobbles: int = None,
    releases_not_before: date = None,
) -> None:
    with get_session() as session:
        repo = AppUserRepository(session)
        repo.create_or_update_user_settings(
            id_user, username, min_scrobbles, releases_not_before
        )


def create_user(lastfm_username: str) -> AppUser:
    with get_session() as session:
        repo = AppUserRepository(session)
        return repo.create_user(lastfm_username)


def get_user_artists(id_user: int) -> list[Row[tuple[Any]]]:
    with get_session() as session:
        repo = ArtistRepository(session)
        return repo.get_artists(id_user)


def delete_user(id_user: int) -> None:
    with get_session() as session:
        repo = AppUserRepository(session)
        repo.delete(id_user)


def update_user(new_username: str, id_user: int) -> None:
    with get_session() as session:
        repo = AppUserRepository(session)
        repo.update(id_user, username=new_username)
