from __future__ import annotations

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent, TabPane

from pages.artist.artist_page import ArtistPage
from pages.release.release_page import ReleasePage
from pages.user.user_page import UserPage


class MainApp(App[None]):
    theme: str = 'textual-light'
    CSS_PATH: ClassVar[list[str]] = [
        'pages/user/user_page.tcss',
        'pages/artist/artist_page.tcss',
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
        yield Footer()


if __name__ == '__main__':
    MainApp().run()
