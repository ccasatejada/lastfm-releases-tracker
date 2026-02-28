from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import DataTable
from textual.widgets._data_table import RowKey

from model.model import AppUser
from pages.user.component.add_user import AddUserBar
from pages.user.component.confirm_delete import ConfirmDeleteScreen
from utils.date_utils import format_datetime


class UserListSection(Vertical):
    class Selected(Message):
        def __init__(self, id_user: int, lastfm_username: str) -> None:
            super().__init__()
            self.id_user = id_user
            self.lastfm_username = lastfm_username

    class DeleteRequested(Message):
        def __init__(self, id_user: int) -> None:
            super().__init__()
            self.id_user = id_user

    def compose(self) -> ComposeResult:
        yield AddUserBar(id='add-user-bar')
        yield DataTable(id='user-list-table')

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column('ID', key='col_id')
        table.add_column('Last.fm', key='col_lastfm')
        table.add_column('Username', key='col_username')
        table.add_column('Artists', key='col_artists')
        table.add_column('Created', key='col_created')
        table.add_column('Updated', key='col_updated')
        table.add_column('', key='col_delete', width=4)

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
        if col_key == 'col_delete':
            row_key = event.cell_key.row_key
            self._request_delete(row_key)

    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        row_key = event.cell_key.row_key
        row_data = self.query_one(DataTable).get_row(row_key)
        id_user = int(row_data[0])
        lastfm_username = str(row_data[1])
        self.post_message(self.Selected(id_user, lastfm_username))

    def _request_delete(self, row_key: RowKey) -> None:
        table = self.query_one(DataTable)
        row_data = table.get_row(row_key)
        id_user = int(row_data[0])

        def _on_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            table.remove_row(row_key)
            self.post_message(self.DeleteRequested(id_user))

        self.app.push_screen(ConfirmDeleteScreen(), _on_confirm)
