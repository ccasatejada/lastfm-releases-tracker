from __future__ import annotations

import logging

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal

from pages.artist.component.artist_detail import ArtistDetailSection
from pages.artist.component.artist_list import ArtistListSection
from service import artist_service

logger = logging.getLogger(__name__)


class ArtistPage(Horizontal):
    def compose(self) -> ComposeResult:
        logger.info('Loading Artist Page')
        yield ArtistListSection(id='artist-list-section')
        yield ArtistDetailSection(id='artist-detail-section')

    def on_mount(self) -> None:
        self._load_artists()

    @work(thread=True)
    def _load_artists(self) -> None:
        rows = artist_service.get_all_artists_with_counts()
        self.app.call_from_thread(self.query_one(ArtistListSection).load_artists, rows)

    def on_artist_list_section_selected(
        self, event: ArtistListSection.Selected
    ) -> None:
        self._load_artist_detail(event.artist_id)

    @work(thread=True, exclusive=True, group='artist-detail')
    def _load_artist_detail(self, artist_id: int) -> None:
        artist, users, releases = artist_service.get_artist_detail(artist_id)
        self.app.call_from_thread(
            self.query_one(ArtistDetailSection).show_artist,
            artist,
            users,
            releases,
        )
