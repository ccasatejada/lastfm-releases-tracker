from __future__ import annotations

import logging
from pathlib import PurePath
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent, TabPane

from pages.artist.artist_page import ArtistPage
from pages.log.log_page import LogPane
from pages.release.release_page import ReleasePage
from pages.user.user_page import UserPage


class MainApp(App[None]):
    theme: str = 'textual-light'
    CSS_PATH: ClassVar[str | PurePath | list[str | PurePath] | None] = [
        'pages/user/user_page.tcss',
        'pages/artist/artist_page.tcss',
        'pages/log/log_page.tcss',
        'pages/release/release_page.tcss',
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane('Releases', id='tab-releases'):
                yield ReleasePage()
            with TabPane('Artists', id='tab-artists'):
                yield ArtistPage()
            with TabPane('Users', id='tab-users'):
                yield UserPage()
            with TabPane('Logs', id='tab-logs'):
                yield LogPane(level=logging.INFO)
        yield Footer()


if __name__ == '__main__':
    MainApp().run()
