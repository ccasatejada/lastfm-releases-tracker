from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from model.internal.base_repository import BaseRepository
from model.model import Artist


class ArtistRepository(BaseRepository[Artist]):

    def __init__(self, session: Session):
        super().__init__(session, Artist)

    def search_by_name(self, name: str) -> List[Artist]:
        """Recherche des artistes par nom (LIKE)"""
        stmt = select(Artist).where(Artist.artist_name.ilike(f"%{name}%"))
        return list(self.session.scalars(stmt))

    def get_with_releases(self, artist_id: int) -> Optional[Artist]:
        """Récupère un artiste avec ses releases"""
        stmt = (
            select(Artist)
            .where(Artist.id == artist_id)
            .options(selectinload(Artist.releases))
        )
        return self.session.scalar(stmt)
