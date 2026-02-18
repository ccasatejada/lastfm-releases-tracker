from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Log


class FetchAllReleases(Vertical):
    def compose(self) -> ComposeResult:
        yield Label('Releases fetched: 0', id='fetch-all-releases-counter')
        yield Log(id='fetch-all-releases-log', auto_scroll=True)

    def reset(self) -> None:
        self.query_one('#fetch-all-releases-counter', Label).update(
            'Releases fetched: 0'
        )
        self.query_one('#fetch-all-releases-log', Log).clear()

    def add_release(self, artist_name: str, release_title: str, nb_tracks: int) -> None:
        log = self.query_one('#fetch-all-releases-log', Log)
        log.write_line(f'- {artist_name} : {release_title} ({nb_tracks:,} tracks)')

        self.query_one('#fetch-all-releases-counter', Label).update(
            f'Releases fetched: {log.line_count}'
        )
