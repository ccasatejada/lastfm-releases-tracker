from sqlalchemy import (
    String, Integer, Boolean, Date, DateTime, ForeignKey, func
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)
from datetime import datetime, date, timedelta
from typing import List


class Base(DeclarativeBase):
    pass


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
    user_settings: Mapped["AppUserSettings"] = relationship(back_populates="user", cascade="all, delete-orphan")


class AppUserSettings(Base, TimestampMixin):
    __tablename__ = 'app_user_settings'

    id: Mapped[int] = mapped_column(primary_key=True)
    min_scrobbles: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    releases_not_before: Mapped[date] = mapped_column(
        Date,
        default=date.today() - timedelta(days=365 * 3),
        nullable=False
    )
    id_user: Mapped[int] = mapped_column(
        ForeignKey('app_users.id', ondelete='CASCADE'),
        nullable=False
    )

    user: Mapped["AppUser"] = relationship(back_populates="user_settings")


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
    __tablename__ = 'app_user_artists'

    id_user: Mapped[int] = mapped_column(
        ForeignKey('app_users.id', ondelete='CASCADE'),
        primary_key=True
    )
    id_artist: Mapped[int] = mapped_column(
        ForeignKey('artists.id', ondelete='CASCADE'),
        primary_key=True
    )

    ignored: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    nb_scrobbles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["AppUser"] = relationship(back_populates="user_artists")
    artist: Mapped["Artist"] = relationship(back_populates="user_artists")


class AppUserRelease(Base, TimestampMixin):
    __tablename__ = 'app_user_releases'

    id_user: Mapped[int] = mapped_column(
        ForeignKey('app_users.id', ondelete='CASCADE'),
        primary_key=True
    )
    id_release: Mapped[int] = mapped_column(
        ForeignKey('releases.id', ondelete='CASCADE'),
        primary_key=True
    )

    ignored: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    nb_scrobbles: Mapped[int | None] = mapped_column(Integer)

    user: Mapped["AppUser"] = relationship(back_populates="user_releases")
    release: Mapped["Release"] = relationship(back_populates="user_releases")