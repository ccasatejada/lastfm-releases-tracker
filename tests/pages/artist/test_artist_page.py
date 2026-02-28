import asyncio
from datetime import datetime
from unittest.mock import patch

from textual.app import App, ComposeResult
from textual.widgets import DataTable

from model.model import Artist
from pages.artist.artist_page import ArtistPage
from pages.artist.component.artist_detail import ArtistDetailSection
from pages.artist.component.artist_list import ArtistListSection


class _App(App):
    def compose(self) -> ComposeResult:
        yield ArtistPage()


def _make_artist(id: int, name: str) -> Artist:
    artist = Artist(id=id, artist_name=name)
    artist.created_at = datetime(2024, 1, 1)
    artist.updated_at = datetime(2024, 1, 1)
    artist.releases = []
    return artist


class TestArtistPage:
    def test_compose_mounts_list_and_detail_sections(self):
        async def _test():
            with patch('pages.artist.artist_page.artist_service') as mock_svc:
                mock_svc.get_all_artists_with_counts.return_value = []
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    return (
                        pilot.app.query_one(ArtistListSection) is not None,
                        pilot.app.query_one(ArtistDetailSection) is not None,
                    )

        has_list, has_detail = asyncio.run(_test())
        assert has_list
        assert has_detail

    def test_get_all_artists_called_on_mount(self):
        async def _test():
            with patch('pages.artist.artist_page.artist_service') as mock_svc:
                mock_svc.get_all_artists_with_counts.return_value = []
                async with _App().run_test(size=(120, 40)):
                    await asyncio.sleep(0.1)
                    return mock_svc.get_all_artists_with_counts.called

        assert asyncio.run(_test())

    def test_artists_loaded_into_table_on_mount(self):
        row = (1, 'Radiohead', 5, 2, datetime(2024, 1, 1), datetime(2024, 2, 1))
        artist = _make_artist(1, 'Radiohead')

        async def _test():
            with patch('pages.artist.artist_page.artist_service') as mock_svc:
                mock_svc.get_all_artists_with_counts.return_value = [row]
                # auto-highlight on first row triggers a detail load
                mock_svc.get_artist_detail.return_value = (artist, [], [])
                async with _App().run_test(size=(120, 40)) as pilot:
                    await asyncio.sleep(0.1)
                    await pilot.pause()
                    count = pilot.app.query_one(DataTable).row_count
                    await pilot.app.workers.wait_for_complete()
                    return count

        assert asyncio.run(_test()) == 1

    def test_artist_selection_triggers_detail_load(self):
        artist = _make_artist(1, 'Radiohead')

        async def _test():
            with patch('pages.artist.artist_page.artist_service') as mock_svc:
                mock_svc.get_all_artists_with_counts.return_value = []
                mock_svc.get_artist_detail.return_value = (artist, [], [])
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    page = pilot.app.query_one(ArtistPage)
                    page._load_artist_detail(1)
                    await asyncio.sleep(0.1)
                    return (
                        mock_svc.get_artist_detail.called,
                        mock_svc.get_artist_detail.call_args,
                    )

        was_called, call_args = asyncio.run(_test())
        assert was_called
        assert call_args.args[0] == 1
