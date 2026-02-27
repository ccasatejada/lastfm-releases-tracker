from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from model.internal.base_repository import BaseRepository
from model.model import AppUser, AppUserArtist, AppUserSettings


class AppUserRepository(BaseRepository[AppUser]):
    def __init__(self, session: Session):
        super().__init__(session, AppUser)

    def get_by_lastfm_username(self, lastfm_username: str) -> AppUser | None:
        stmt = select(AppUser).where(AppUser.lastfm_username == lastfm_username)
        return self.session.scalar(stmt)

    def get_with_artists(self, id_user: int) -> AppUser | None:
        stmt = (
            select(AppUser)
            .where(AppUser.id == id_user)
            .options(selectinload(AppUser.user_artists))
        )
        return self.session.scalar(stmt)

    def get_users(
        self,
    ) -> tuple[
        dict[Any, Any] | dict[str, Any] | dict[str, str] | dict[bytes, bytes],
        list[AppUser],
    ]:
        users = self.get_all()
        stmt = select(AppUserArtist.id_user, func.count()).group_by(
            AppUserArtist.id_user
        )
        counts = dict(self.session.execute(stmt).all())
        return counts, users

    def get_user_with_settings(
        self, id_user: int
    ) -> tuple[AppUser, AppUserSettings | None]:
        stmt = (
            select(AppUser)
            .where(AppUser.id == id_user)
            .options(selectinload(AppUser.user_settings))
        )
        user = self.session.scalar(stmt)
        if not user:
            raise ValueError(f'User with id {id_user} not found')
        settings = user.user_settings
        return user, settings

    def create_user(self, lastfm_username: str) -> AppUser:
        existing_user = self.get_by_lastfm_username(lastfm_username)
        if existing_user:
            self.create_or_update_user_settings(
                existing_user.id, existing_user.username
            )
            return existing_user

        user = self.create(lastfm_username=lastfm_username)
        self.session.flush()
        self.create_or_update_user_settings(user.id)
        return user

    def create_or_update_user_settings(
        self,
        id_user: int,
        username: str | None = None,
        min_scrobbles: int | None = None,
        releases_not_before: date | None = None,
    ) -> None:
        stmt = (
            select(AppUser)
            .where(AppUser.id == id_user)
            .options(selectinload(AppUser.user_settings))
        )
        user: AppUser = self.session.scalar(stmt)  # type: ignore[assignment]
        user.username = username

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
        self.session.flush()
