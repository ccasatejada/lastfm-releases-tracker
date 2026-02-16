from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Log


class FetchReleases(Vertical):

    def compose(self) -> ComposeResult:
        yield Label('Releases fetched: 0', id='fetch-release-counter')
        yield Log(id='fetch-release-log', auto_scroll=True)

    def reset(self) -> None:
        self.query_one('#fetch-release-counter', Label).update('Releases fetched: 0')
        self.query_one('#fetch-release-log', Log).clear()

    def add_release(self, release_title: str, nb_tracks: int) -> None:
        log = self.query_one('#fetch-release-log', Log)
        log.write_line(f'- {release_title} ({nb_tracks:,} tracks)')

        self.query_one('#fetch-release-counter', Label).update(f'Releases fetched: {log.line_count}')
