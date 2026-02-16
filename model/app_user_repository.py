from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from model.internal.base_repository import BaseRepository
from model.model import AppUser


class AppUserRepository(BaseRepository[AppUser]):
    def __init__(self, session: Session):
        super().__init__(session, AppUser)

    def get_by_lastfm_username(self, lastfm_username: str) -> Optional[AppUser]:
        stmt = select(AppUser).where(AppUser.lastfm_username == lastfm_username)
        return self.session.scalar(stmt)

    def get_with_artists(self, id_user: int) -> Optional[AppUser]:
        stmt = (
            select(AppUser)
            .where(AppUser.id == id_user)
            .options(selectinload(AppUser.user_artists))
        )
        return self.session.scalar(stmt)