from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Label, Static


class FetchArtists(Vertical):

    def compose(self) -> ComposeResult:
        yield Label('Artists fetched: 0', id='fetch-counter')
        yield VerticalScroll(id='fetch-log')

    def reset(self) -> None:
        self.query_one('#fetch-counter', Label).update('Artists fetched: 0')
        self.query_one('#fetch-log', VerticalScroll).remove_children()
        self.add_class('hidden')

    def add_artist(self, artist_name: str, nb_scrobbles: int, count: int) -> None:
        self.remove_class('hidden')
        self.query_one('#fetch-counter', Label).update(f'Artists fetched: {count}')
        log = self.query_one('#fetch-log', VerticalScroll)
        log.mount(Static(f'- {artist_name} ({nb_scrobbles:,} scrobbles)'))
        log.scroll_end(animate=False)
