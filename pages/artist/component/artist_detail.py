from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Label, Static, Rule

from model.model import AppUser, Artist, Release
from utils.date_utils import format_date
from utils.thumbnail_utils import get_thumbnail


class ArtistDetailSection(Vertical):

    def compose(self) -> ComposeResult:
        yield Static('Select an artist', id='detail-placeholder')

    async def show_artist(self, artist: Artist, users: list[AppUser], releases: list[Release]) -> None:
        await self.remove_children()
        # Header: thumbnail + name
        header_children: list[Static | Label] = []
        thumb_path = Path(f'files/artists_thumbnails/{artist.id}.jpg')
        if thumb_path.exists():
            header_children.append(
                Static(get_thumbnail(thumb_path, resize=(30, 30)), id='artist-thumb')
            )

        # Users sub-section
        usernames = ', '.join(u.lastfm_username for u in users) if users else 'None'

        # Releases sub-section
        table = DataTable(id='release-table')
        # Mount everything at once so all parents are attached first
        await self.mount_all([
            Horizontal(*header_children, id='artist-header'),
            Label(artist.artist_name or '', id='artist-name'),
            Rule(),
            Label('Releases', classes='section-title'),
            table,
            Rule(),
            Label('Users', classes='section-title'),
            Static(usernames, id='artist-users')
        ])

        table.add_column('Cover', key='col_cover', width=4)
        table.add_column('Title', key='col_title')
        table.add_column('Date', key='col_date')
        table.add_column('Length', key='col_length')
        table.add_column('Tracks', key='col_tracks')

        for release in releases:
            mins, secs = divmod(release.length, 60)
            table.add_row(
                '▣',
                release.release_title,
                format_date(release.release_date),
                f'{mins}:{secs:02d}',
                str(release.nb_tracks),
                key=f'release_{release.id}',
            )
