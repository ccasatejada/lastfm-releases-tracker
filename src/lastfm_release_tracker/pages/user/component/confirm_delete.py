from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmDeleteScreen(ModalScreen[bool]):
    BINDINGS = [('escape', 'cancel', 'Cancel')]

    def compose(self) -> ComposeResult:
        with Vertical(id='confirm-dialog'):
            yield Label('Are you sure?', id='confirm-question')
            with Horizontal(id='confirm-buttons'):
                yield Button('Cancel', id='cancel-btn', variant='default')
                yield Button('OK', id='ok-btn', variant='default')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'ok-btn':
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)
