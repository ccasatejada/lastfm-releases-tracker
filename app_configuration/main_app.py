from __future__ import annotations

import logging
import os
from pathlib import Path, PurePath
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent, TabPane

from pages.artist.artist_page import ArtistPage
from pages.log.log_page import LogPane
from pages.release.release_page import ReleasePage
from pages.user.user_page import UserPage

# resolved via this package's own (editable-linked) file location rather than
# main.py's, since main.py gets physically copied into site-packages when
# installed as a uv tool and would no longer sit next to pages/, files/, .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class MainApp(App[None]):
    theme: str = 'textual-light'
    CSS_PATH: ClassVar[str | PurePath | list[str | PurePath] | None] = [
        PROJECT_ROOT / 'pages/user/user_page.tcss',
        PROJECT_ROOT / 'pages/artist/artist_page.tcss',
        PROJECT_ROOT / 'pages/log/log_page.tcss',
        PROJECT_ROOT / 'pages/release/release_page.tcss',
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
    os.chdir(PROJECT_ROOT)
    MainApp().run()
