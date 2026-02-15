from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class ReleasePage(Vertical):

    def compose(self) -> ComposeResult:
        yield Static('Releases — coming soon')
