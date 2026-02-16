from __future__ import annotations

from datetime import date

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Input, Label, Select, Static, Rule

from model.model import AppUserSettings
from pages.user.component.fetch_all_releases import FetchAllReleases
from pages.user.component.fetch_artists import FetchArtists
from pages.user.component.fetch_releases import FetchReleases


class UserDetailSection(Vertical):

    _current_id_user: int | None = None
    _lastfm_username: str = ''

    class FetchRequested(Message):
        def __init__(self, lastfm_username: str, lastfm_password: str) -> None:
            super().__init__()
            self.lastfm_username = lastfm_username
            self.lastfm_password = lastfm_password

    class FetchReleasesRequested(Message):
        def __init__(self, lastfm_username: str, lastfm_password: str, id_artist: int) -> None:
            super().__init__()
            self.lastfm_username = lastfm_username
            self.lastfm_password = lastfm_password
            self.id_artist = id_artist

    class FetchAllReleasesRequested(Message):
        def __init__(self, lastfm_username: str, lastfm_password: str) -> None:
            super().__init__()
            self.lastfm_username = lastfm_username
            self.lastfm_password = lastfm_password

    class SettingsChanged(Message):
        def __init__(self, id_user: int, min_scrobbles: int, releases_not_before: date) -> None:
            super().__init__()
            self.id_user = id_user
            self.min_scrobbles = min_scrobbles
            self.releases_not_before = releases_not_before

    def compose(self) -> ComposeResult:
        yield Static('Select a user', id='detail-placeholder')
        with VerticalScroll(id='detail-content', classes='hidden'):
            # settings
            yield Label('Minimum scrobbles', classes='setting-label')
            yield Input(placeholder='1000', id='min-scrobbles-input', type='integer')
            yield Label('Releases not before', classes='setting-label')
            yield Input(placeholder='YYYY-MM-DD', id='releases-not-before-input')
            with Horizontal(id='submit-form'):
                yield Button('Save', id='save-button', variant='primary')

            yield Rule()

            yield Input(placeholder='Last.fm password', password=True, id='password-input')

            yield Rule()

            with Horizontal(id='fetch-bar'):
                yield Button('Fetch artists', id='fetch-button', variant='primary')
            yield FetchArtists(id='fetch-progress')

            yield Rule()

            with Horizontal(id='fetch-all-releases-bar'):
                yield Button('Fetch all releases', id='fetch-all-releases-button', variant='primary')
            yield FetchAllReleases(id='fetch-all-releases')

            yield Rule()

            with Horizontal(id='fetch-release-bar'):
                yield Select([], id='artist-select', prompt='Select an artist')
                yield Button('Fetch releases', id='fetch-release-button', variant='primary')
            yield FetchReleases(id='fetch-release')

    def show_user(
        self,
        lastfm_username: str,
        id_user: int,
        settings: AppUserSettings | None,
        env_password: str | None,
        artists: list[tuple[int, str]] | None = None,
    ) -> None:
        self._current_id_user = id_user
        self._lastfm_username = lastfm_username
        self.query_one('#detail-placeholder').add_class('hidden')
        self.query_one('#detail-content').remove_class('hidden')
        self.query_one('#password-input', Input).value = env_password or ''

        min_input = self.query_one('#min-scrobbles-input', Input)
        rnb_input = self.query_one('#releases-not-before-input', Input)

        if settings:
            min_input.value = str(settings.min_scrobbles)
            rnb_input.value = str(settings.releases_not_before)
        else:
            min_input.value = ''
            rnb_input.value = ''

        artist_select = self.query_one('#artist-select', Select)
        if artists:
            artist_select.set_options([(name, id_artist) for id_artist, name in artists])
        else:
            artist_select.set_options([])

        self.query_one(FetchArtists).reset()
        self.query_one(FetchReleases).reset()

    def _toggle_fetch(self, fetch_button_id: str, label: str, fetching: bool):
        btn = self.query_one(f'#{fetch_button_id}', Button)
        if fetching:
            btn.disabled = True
            btn.label = 'Fetching...'
        else:
            btn.label = f'Fetch {label}'
            btn.disabled = False

    def set_fetching(self, fetching: bool) -> None:
        self._toggle_fetch('fetch-button', 'artists', fetching)

    def set_fetching_releases(self, fetching: bool) -> None:
        self._toggle_fetch('fetch-release-button', 'releases', fetching)

    def set_fetching_all_releases(self, fetching: bool) -> None:
        self._toggle_fetch('fetch-all-releases-button', 'all releases', fetching)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'save-button':
            self._submit_settings()
        elif event.button.id == 'fetch-button':
            self._request_fetch_artists()
        elif event.button.id == 'fetch-release-button':
            self._request_fetch_releases()
        elif event.button.id == 'fetch-all-releases-button':
            self._request_fetch_all_releases()
        event.stop()

    def _submit_settings(self) -> None:
        min_str = self.query_one('#min-scrobbles-input', Input).value.strip()
        rnb_str = self.query_one('#releases-not-before-input', Input).value.strip()
        try:
            min_scrobbles = int(min_str) if min_str else 1000
            releases_not_before = date.fromisoformat(rnb_str) if rnb_str else date.today()
        except (ValueError, TypeError):
            self.app.notify('Invalid settings values', severity='error')
            return
        self.post_message(
            self.SettingsChanged(self._current_id_user, min_scrobbles, releases_not_before)
        )

    def _request_fetch_artists(self) -> None:
        password = self.query_one('#password-input', Input).value
        if not password:
            return
        self.set_fetching(True)
        self.query_one(FetchArtists).reset()
        self.post_message(self.FetchRequested(self._lastfm_username, password))

    def _request_fetch_releases(self) -> None:
        password = self.query_one('#password-input', Input).value
        if not password:
            return
        artist_select = self.query_one('#artist-select', Select)
        if artist_select.value is Select.BLANK:
            self.app.notify('Select an artist first', severity='warning')
            return
        self.set_fetching_releases(True)
        self.query_one(FetchReleases).reset()
        self.post_message(
            self.FetchReleasesRequested(self._lastfm_username, password, artist_select.value)
        )

    def _request_fetch_all_releases(self) -> None:
        password = self.query_one('#password-input', Input).value
        if not password:
            return
        self.set_fetching_all_releases(True)
        self.query_one(FetchAllReleases).reset()
        self.post_message(
            self.FetchAllReleasesRequested(self._lastfm_username, password)
        )
