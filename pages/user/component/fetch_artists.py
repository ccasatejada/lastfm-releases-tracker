from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Log


class FetchArtists(Vertical):
    def compose(self) -> ComposeResult:
        yield Label('Artists fetched: 0', id='fetch-counter')
        yield Log(id='fetch-log', auto_scroll=True)

    def reset(self) -> None:
        self.query_one('#fetch-counter', Label).update('Artists fetched: 0')
        self.query_one('#fetch-log', Log).clear()

    def add_artist(self, artist_name: str, nb_scrobbles: int) -> None:
        log = self.query_one('#fetch-log', Log)
        log.write_line(f'- {artist_name} ({nb_scrobbles:,} scrobbles)')

        self.query_one('#fetch-counter', Label).update(
            f'Artists fetched: {log.line_count}'
        )
