from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import DataTable

from utils.date_utils import format_datetime


class ArtistListSection(Vertical):
    class Selected(Message):
        def __init__(self, artist_id: int) -> None:
            super().__init__()
            self.artist_id = artist_id

    def compose(self) -> ComposeResult:
        yield DataTable(id='artist-table')

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column('ID', key='col_id')
        table.add_column('Artist name', key='col_name')
        table.add_column('Releases', key='col_releases')
        table.add_column('Users', key='col_users')
        table.add_column('Created', key='col_created')
        table.add_column('Updated', key='col_updated')
        table.cursor_type = 'row'

    def load_artists(self, rows: list[tuple[Any, ...]]) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for artist_id, name, nb_releases, nb_users, created_at, updated_at in rows:
            table.add_row(
                str(artist_id),
                name or '',
                str(nb_releases),
                str(nb_users),
                format_datetime(created_at),
                format_datetime(updated_at),
                key=f'artist_{artist_id}',
            )

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self._get_artist_detail(event)

    def _get_artist_detail(self, event: DataTable.RowHighlighted) -> None:
        row_data = self.query_one(DataTable).get_row(event.row_key)
        artist_id = int(row_data[0])
        self.post_message(self.Selected(artist_id))
