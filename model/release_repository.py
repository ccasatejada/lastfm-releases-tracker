from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from model.internal.base_repository import BaseRepository
from model.model import Release


class ReleaseRepository(BaseRepository[Release]):
    """Repository pour Release"""

    def __init__(self, session: Session):
        super().__init__(session, Release)

    def get_by_artist(self, artist_id: int) -> List[Release]:
        """Récupère toutes les releases d'un artiste"""
        stmt = (
            select(Release)
            .where(Release.id_artist == artist_id)
            .order_by(Release.release_date.desc())
        )
        return list(self.session.scalars(stmt))

    def get_recent(self, limit: int = 10) -> List[Release]:
        """Récupère les releases les plus récentes"""
        stmt = (
            select(Release)
            .order_by(Release.release_date.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))