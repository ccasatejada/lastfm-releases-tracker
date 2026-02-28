from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import DataTable

from utils.date_utils import compute_length, format_date


class ReleaseListSection(Vertical):
    class Selected(Message):
        def __init__(self, release_id: int) -> None:
            super().__init__()
            self.release_id = release_id

    def compose(self) -> ComposeResult:
        yield DataTable(id='releases-list-table')

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column('Date', key='col_date', width=12)
        table.add_column('Artist', key='col_artist', width=20)
        table.add_column('Title', key='col_title', width=30)
        table.add_column('Length', key='col_length', width=8)
        table.add_column('Tracks', key='col_tracks', width=7)
        table.add_column('URL', key='col_url', width=30)
        table.cursor_type = 'row'

    def load_releases(self, rows: list[tuple[Any, ...]]) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for (
            release_id,
            artist_name,
            title,
            release_date,
            length,
            nb_tracks,
            url,
        ) in rows:
            mins, secs = compute_length(length)
            table.add_row(
                format_date(release_date),
                artist_name,
                title,
                f'{mins}:{secs:02d}',
                str(nb_tracks),
                url,
                key=f'release_{release_id}',
            )

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None or event.row_key.value is None:
            return
        release_id = int(event.row_key.value.split('_', 1)[1])
        self.post_message(self.Selected(release_id))
