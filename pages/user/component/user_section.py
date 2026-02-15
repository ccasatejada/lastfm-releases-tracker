from __future__ import annotations

from datetime import datetime

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, DataTable, Input

from pages.user.component.confirm_delete import ConfirmDeleteScreen
from pages.user.component.fetch_artists import FetchArtists
from model.model import AppUser
from utils.date_utils import format_datetime


class UserSection(Vertical):
    _env_username: str | None = None
    _env_password: str | None = None
    _editing_row_key: object | None = None

    class FetchRequested(Message):
        def __init__(self, lastfm_username: str, lastfm_password: str) -> None:
            super().__init__()
            self.lastfm_username = lastfm_username
            self.lastfm_password = lastfm_password

    class DeleteRequested(Message):
        def __init__(self, user_id: int) -> None:
            super().__init__()
            self.user_id = user_id

    class EditSaved(Message):
        def __init__(self, user_id: int, new_username: str) -> None:
            super().__init__()
            self.user_id = user_id
            self.new_username = new_username

    def compose(self) -> ComposeResult:
        yield DataTable(id='user-table')
        with Horizontal(id='edit-bar'):
            yield Input(placeholder='Username', id='edit-input')
            yield Button('Save', id='save-edit-btn', variant='primary')
        yield Input(
            placeholder='Last.fm password',
            password=True,
            id='password-input',
        )
        with Horizontal(id='fetch-bar'):
            yield Button('Fetch artists', id='fetch-btn', variant='success', disabled=True)
        with Horizontal(id='artists-fetch-logs'):
            yield FetchArtists(id='fetch-progress')

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column('ID', key='col_id')
        table.add_column('Last.fm', key='col_lastfm')
        table.add_column('Username', key='col_username')
        table.add_column('Artists', key='col_artists')
        table.add_column('Created', key='col_created')
        table.add_column('Updated', key='col_updated')
        table.add_column('', key='col_delete', width=4)
        self.query_one('#edit-bar').add_class('hidden')
        self.query_one('#password-input').add_class('hidden')
        self.query_one('#fetch-bar').add_class('hidden')
        self.query_one(FetchArtists).add_class('hidden')

    def set_env_credentials(self, username: str, password: str) -> None:
        self._env_username = username
        self._env_password = password

    def add_user(self, user: AppUser, nb_artists: int = 0) -> None:
        table = self.query_one(DataTable)
        row_key = f'user_{user.id}'
        for key in table.rows:
            if key.value == row_key:
                return
        table.add_row(
            str(user.id),
            user.lastfm_username,
            user.username or '',
            str(nb_artists),
            format_datetime(user.created_at),
            format_datetime(user.updated_at),
            '✕',
            key=row_key,
        )

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        col_key = event.cell_key.column_key
        if col_key == 'col_username':
            self._start_edit(event.cell_key.row_key)
        elif col_key == 'col_delete':
            self._request_delete(event.cell_key.row_key)
        else:
            self._select_user(event.cell_key.row_key)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self._select_user(event.row_key)

    def _select_user(self, row_key: object) -> None:
        if row_key is None:
            return
        self._show_fetch_area()
        row_data = self.query_one(DataTable).get_row(row_key)
        lastfm_username = str(row_data[1])
        pwd_input = self.query_one('#password-input', Input)
        if (
            self._env_username
            and lastfm_username == self._env_username
            and self._env_password
        ):
            pwd_input.value = self._env_password
        else:
            pwd_input.value = ''

    def _show_fetch_area(self) -> None:
        self.query_one('#edit-bar').add_class('hidden')
        self.query_one('#password-input').remove_class('hidden')
        self.query_one('#fetch-bar').remove_class('hidden')

    def _start_edit(self, row_key: object) -> None:
        table = self.query_one(DataTable)
        row_data = table.get_row(row_key)
        self._editing_row_key = row_key

        edit_input = self.query_one('#edit-input', Input)
        edit_input.value = str(row_data[2])  # col_username

        self.query_one('#edit-bar').remove_class('hidden')
        self.query_one('#password-input').add_class('hidden')
        self.query_one('#fetch-bar').add_class('hidden')
        edit_input.focus()

    def _save_edit(self) -> None:
        if self._editing_row_key is None:
            return
        table = self.query_one(DataTable)
        new_username = self.query_one('#edit-input', Input).value.strip()
        row_data = table.get_row(self._editing_row_key)
        user_id = int(row_data[0])
        table.update_cell(self._editing_row_key, 'col_username', new_username)
        self.post_message(self.EditSaved(user_id, new_username))
        self._editing_row_key = None
        self._show_fetch_area()

    def _request_delete(self, row_key: object) -> None:
        table = self.query_one(DataTable)
        row_data = table.get_row(row_key)
        user_id = int(row_data[0])

        def _on_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            if self._editing_row_key == row_key:
                self._editing_row_key = None
            table.remove_row(row_key)
            self.post_message(self.DeleteRequested(user_id))
            if table.row_count == 0:
                self.query_one('#edit-bar').add_class('hidden')
                self.query_one('#password-input').add_class('hidden')
                self.query_one('#fetch-bar').add_class('hidden')

        self.app.push_screen(ConfirmDeleteScreen(), _on_confirm)

    @on(Input.Changed, '#password-input')
    def _on_password_changed(self) -> None:
        self._update_fetch_btn()

    @on(Input.Submitted, '#edit-input')
    def _on_edit_submitted(self) -> None:
        self._save_edit()

    def _update_fetch_btn(self) -> None:
        password = self.query_one('#password-input', Input).value
        btn = self.query_one('#fetch-btn', Button)
        btn.disabled = len(password) < 6

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'save-edit-btn':
            self._save_edit()
            event.stop()
        elif event.button.id == 'fetch-btn':
            table = self.query_one(DataTable)
            if table.row_count > 0:
                row_data = table.get_row_at(table.cursor_row)
                lastfm_username = str(row_data[1])
                lastfm_password = self.query_one('#password-input', Input).value
                self.set_fetching(True)
                self.query_one(FetchArtists).reset()
                self.post_message(self.FetchRequested(lastfm_username, lastfm_password))
            event.stop()

    def set_fetching(self, fetching: bool) -> None:
        btn = self.query_one('#fetch-btn', Button)
        if fetching:
            btn.disabled = True
            btn.label = 'Fetching...'
        else:
            btn.label = 'Fetch artists'
            self._update_fetch_btn()
