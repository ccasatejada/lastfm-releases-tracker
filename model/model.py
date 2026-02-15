from sqlalchemy import (
    String, Integer, Boolean, Date, DateTime, ForeignKey, func
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)
from datetime import datetime, date
from typing import List


class Base(DeclarativeBase):
    pass


# Mixin pour les timestamps communs
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class AppUser(Base, TimestampMixin):
    __tablename__ = 'app_users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255))
    lastfm_username: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relations
    user_artists: Mapped[List["AppUserArtist"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    user_releases: Mapped[List["AppUserRelease"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Artist(Base, TimestampMixin):
    __tablename__ = 'artists'

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_name: Mapped[str | None] = mapped_column(String(255))
    artist_url: Mapped[str | None] = mapped_column(String(500))
    # Relations
    releases: Mapped[List["Release"]] = relationship(
        back_populates="artist",
        cascade="all, delete-orphan"
    )
    user_artists: Mapped[List["AppUserArtist"]] = relationship(
        back_populates="artist",
        cascade="all, delete-orphan"
    )


class Release(Base, TimestampMixin):
    __tablename__ = 'releases'

    id: Mapped[int] = mapped_column(primary_key=True)
    release_title: Mapped[str] = mapped_column(String(255), nullable=False)
    release_date: Mapped[date] = mapped_column(Date, nullable=False)
    length: Mapped[int] = mapped_column(Integer, nullable=False)  # en secondes ?
    nb_tracks: Mapped[int] = mapped_column(Integer, nullable=False)
    release_url: Mapped[str | None] = mapped_column(String(500))
    # Foreign key CORRECTE
    id_artist: Mapped[int] = mapped_column(
        ForeignKey('artists.id', ondelete='CASCADE'),
        nullable=False
    )

    # Relations
    artist: Mapped["Artist"] = relationship(back_populates="releases")
    user_releases: Mapped[List["AppUserRelease"]] = relationship(
        back_populates="release",
        cascade="all, delete-orphan"
    )


class AppUserArtist(Base, TimestampMixin):
    """Table de liaison many-to-many entre users et artists"""
    __tablename__ = 'app_user_artists'

    # Clé primaire composite - PAS d'auto-increment !
    id_user: Mapped[int] = mapped_column(
        ForeignKey('app_users.id', ondelete='CASCADE'),
        primary_key=True
    )
    id_artist: Mapped[int] = mapped_column(
        ForeignKey('artists.id', ondelete='CASCADE'),
        primary_key=True
    )

    # Colonnes supplémentaires
    ignored: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    nb_scrobbles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relations
    user: Mapped["AppUser"] = relationship(back_populates="user_artists")
    artist: Mapped["Artist"] = relationship(back_populates="user_artists")


class AppUserRelease(Base, TimestampMixin):
    """Table de liaison many-to-many entre users et releases"""
    __tablename__ = 'app_user_releases'

    # Clé primaire composite - PAS d'auto-increment !
    id_user: Mapped[int] = mapped_column(
        ForeignKey('app_users.id', ondelete='CASCADE'),
        primary_key=True
    )
    id_release: Mapped[int] = mapped_column(
        ForeignKey('releases.id', ondelete='CASCADE'),
        primary_key=True
    )

    # Colonnes supplémentaires
    ignored: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    nb_scrobbles: Mapped[int | None] = mapped_column(Integer)

    # Relations
    user: Mapped["AppUser"] = relationship(back_populates="user_releases")
    release: Mapped["Release"] = relationship(back_populates="user_releases")