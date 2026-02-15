from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Input


class AddUserBar(Horizontal):

    class Submitted(Message):
        def __init__(self, username: str) -> None:
            super().__init__()
            self.username = username

    def compose(self) -> ComposeResult:
        yield Input(placeholder='Last.fm username', id='username-input')
        yield Button('OK', id='ok-btn', variant='primary')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'ok-btn':
            self._submit()
            event.stop()

    def on_input_submitted(self) -> None:
        self._submit()

    def _submit(self) -> None:
        inp = self.query_one('#username-input', Input)
        username = inp.value.strip()
        if username:
            self.post_message(self.Submitted(username))
            inp.value = ''
