from __future__ import annotations

import logging

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal

from pages.release.component.release_detail import ReleaseDetailSection
from pages.release.component.release_list import ReleaseListSection
from service import release_service

logger = logging.getLogger(__name__)


class ReleasePage(Horizontal):
    def compose(self) -> ComposeResult:
        logger.info('Loading Release Page')
        yield ReleaseListSection(id='release-list-section')
        yield ReleaseDetailSection(id='release-detail-section')

    def on_mount(self) -> None:
        self._load_releases()

    @work(thread=True)
    def _load_releases(self) -> None:
        rows = release_service.get_all_releases()
        self.app.call_from_thread(
            self.query_one(ReleaseListSection).load_releases, rows
        )

    def on_release_list_section_selected(
        self, event: ReleaseListSection.Selected
    ) -> None:
        self._load_release_detail(event.release_id)

    @work(thread=True, exclusive=True, group='release-detail')
    def _load_release_detail(self, release_id: int) -> None:
        release, artist, user_releases = release_service.get_release_detail(release_id)
        self.app.call_from_thread(
            self.query_one(ReleaseDetailSection).show_release,
            release,
            artist,
            user_releases,
        )
