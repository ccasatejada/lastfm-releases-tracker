from __future__ import annotations

from datetime import date

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, Input, Label, Static

from model.model import AppUserSettings
from pages.user.component.fetch_artists import FetchArtists


class UserDetailSection(Vertical):

    _current_user_id: int | None = None
    _lastfm_username: str = ''

    class FetchRequested(Message):
        def __init__(self, lastfm_username: str, lastfm_password: str) -> None:
            super().__init__()
            self.lastfm_username = lastfm_username
            self.lastfm_password = lastfm_password

    class SettingsChanged(Message):
        def __init__(self, user_id: int, min_scrobbles: int, releases_not_before: date) -> None:
            super().__init__()
            self.user_id = user_id
            self.min_scrobbles = min_scrobbles
            self.releases_not_before = releases_not_before

    def compose(self) -> ComposeResult:
        yield Static('Select a user', id='detail-placeholder')
        with Vertical(id='detail-content', classes='hidden'):
            with Horizontal(id='fetch-bar'):
                yield Input(placeholder='Last.fm password', password=True, id='password-input')
                yield Button('Fetch artists', id='fetch-button', variant='primary')
            yield FetchArtists(id='fetch-progress')
            yield Label('Minimum scrobbles', classes='setting-label')
            yield Input(placeholder='1000', id='min-scrobbles-input', type='integer')
            yield Label('Releases not before', classes='setting-label')
            yield Input(placeholder='YYYY-MM-DD', id='releases-not-before-input')
            with Horizontal(id='submit-form'):
                yield Button('Save', id='save-button', variant='primary')

    def show_user(self, lastfm_username: str,
                  user_id: int,
                  settings: AppUserSettings | None,
                  env_password: str | None) -> None:
        self._current_user_id = user_id
        self._lastfm_username = lastfm_username
        self.query_one('#detail-placeholder').add_class('hidden')
        self.query_one('#detail-content').remove_class('hidden')

        pwd_input = self.query_one('#password-input', Input)
        pwd_input.value = env_password or ''

        min_input = self.query_one('#min-scrobbles-input', Input)
        rnb_input = self.query_one('#releases-not-before-input', Input)

        if settings:
            min_input.value = str(settings.min_scrobbles)
            rnb_input.value = str(settings.releases_not_before)
        else:
            min_input.value = ''
            rnb_input.value = ''

        self.query_one(FetchArtists).reset()

    def set_fetching(self, fetching: bool) -> None:
        btn = self.query_one('#fetch-button', Button)
        if fetching:
            btn.disabled = True
            btn.label = 'Fetching...'
        else:
            btn.label = 'Fetch artists'
            btn.disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'save-button':
            min_str = self.query_one('#min-scrobbles-input', Input).value.strip()
            rnb_str = self.query_one('#releases-not-before-input', Input).value.strip()
            try:
                min_scrobbles = int(min_str) if min_str else 1000
                releases_not_before = date.fromisoformat(rnb_str) if rnb_str else date.today()
            except (ValueError, TypeError):
                self.app.notify('Invalid settings values', severity='error')
                return
            self.post_message(
                self.SettingsChanged(self._current_user_id, min_scrobbles, releases_not_before)
            )
        elif event.button.id == 'fetch-button':
            password = self.query_one('#password-input', Input).value
            if not password:
                return
            self.set_fetching(True)
            self.query_one(FetchArtists).reset()
            self.post_message(self.FetchRequested(self._lastfm_username, password))
        event.stop()
