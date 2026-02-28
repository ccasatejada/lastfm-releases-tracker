from __future__ import annotations

import webbrowser
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, DataTable, Label, Rule, Static

from model.model import AppUserRelease, Artist, Release
from utils.date_utils import compute_length, format_date
from utils.thumbnail_utils import get_thumbnail


class ReleaseDetailSection(Vertical):
    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self._current_url: str | None = None

    def compose(self) -> ComposeResult:
        yield Static('Select a release', id='detail-placeholder')

    async def show_release(
        self, release: Release, artist: Artist, user_releases: list[AppUserRelease]
    ) -> None:
        await self.remove_children()
        self._current_url = release.release_url

        children: list = []

        cover_path = Path(f'files/releases_covers/{release.id_artist}/{release.id}.jpg')
        if cover_path.exists():
            children.append(
                Static(get_thumbnail(cover_path, resize=(20, 20)), id='release-cover')
            )
        else:
            children.append(Static('No cover', id='no-cover-placeholder'))

        mins, secs = compute_length(release.length)
        children.extend(
            [
                Label(artist.artist_name or '', id='release-artist'),
                Label(release.release_title or '', id='release-title'),
                Label(format_date(release.release_date), id='release-date'),
                Label(f'{mins}:{secs:02d}', id='release-length'),
                Label(str(release.nb_tracks), id='release-tracks'),
            ]
        )

        if release.release_url is not None:
            children.extend(
                [
                    Rule(),
                    Static(release.release_url, id='release-url'),
                    Button('Open in browser', id='open-url-button'),
                ]
            )

        user_table = DataTable(id='user-release-table')
        children.extend(
            [
                Rule(),
                Label('Users', classes='section-title'),
                user_table,
            ]
        )

        await self.mount_all(children)

        user_table.add_column('User', key='col_user')
        user_table.add_column('Ignored', key='col_ignored')
        for ur in user_releases:
            user_table.add_row(
                ur.user.lastfm_username,
                str(ur.ignored),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'open-url-button' and self._current_url:
            webbrowser.open_new_tab(self._current_url)
