from __future__ import annotations

import logging
from pathlib import Path, PurePath
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent, TabPane

from lastfm_release_tracker.pages.artist.artist_page import ArtistPage
from lastfm_release_tracker.pages.log.log_page import LogPane
from lastfm_release_tracker.pages.release.release_page import ReleasePage
from lastfm_release_tracker.pages.user.user_page import UserPage

# this package's own file location, so CSS_PATH resolves next to pages/
# regardless of the caller's working directory
PACKAGE_ROOT = Path(__file__).resolve().parent.parent


class MainApp(App[None]):
    theme: str = 'textual-light'
    CSS_PATH: ClassVar[str | PurePath | list[str | PurePath] | None] = [
        PACKAGE_ROOT / 'pages/user/user_page.tcss',
        PACKAGE_ROOT / 'pages/artist/artist_page.tcss',
        PACKAGE_ROOT / 'pages/log/log_page.tcss',
        PACKAGE_ROOT / 'pages/release/release_page.tcss',
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


def main() -> None:
    MainApp().run()
