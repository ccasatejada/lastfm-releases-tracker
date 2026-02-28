import asyncio
from datetime import date
from unittest.mock import patch

from textual.app import App, ComposeResult

from model.model import Artist, Release
from pages.release.component.release_detail import ReleaseDetailSection
from pages.release.component.release_list import ReleaseListSection
from pages.release.release_page import ReleasePage


class _App(App):
    def compose(self) -> ComposeResult:
        yield ReleasePage()


def _make_release(id=1, title='OK Computer') -> Release:
    release = Release(
        id=id,
        release_title=title,
        release_date=date(1997, 6, 16),
        length=3180,
        nb_tracks=12,
        id_artist=1,
    )
    artist = Artist(id=1, artist_name='Radiohead')
    release.artist = artist
    release.user_releases = []
    return release


class TestReleasePage:
    def test_compose_mounts_list_and_detail_sections(self):
        async def _test():
            with patch('pages.release.release_page.release_service') as mock_svc:
                mock_svc.get_all_releases.return_value = []
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    return (
                        pilot.app.query_one(ReleaseListSection) is not None,
                        pilot.app.query_one(ReleaseDetailSection) is not None,
                    )

        has_list, has_detail = asyncio.run(_test())
        assert has_list
        assert has_detail

    def test_get_all_releases_called_on_mount(self):
        async def _test():
            with patch('pages.release.release_page.release_service') as mock_svc:
                mock_svc.get_all_releases.return_value = []
                async with _App().run_test(size=(120, 40)):
                    await asyncio.sleep(0.1)
                    return mock_svc.get_all_releases.called

        assert asyncio.run(_test())

    def test_releases_loaded_into_table_on_mount(self):
        row = (
            1,
            'Radiohead',
            'OK Computer',
            date(1997, 6, 16),
            3180,
            12,
            'https://example.com',
        )
        release = _make_release(1)

        async def _test():
            with patch('pages.release.release_page.release_service') as mock_svc:
                mock_svc.get_all_releases.return_value = [row]
                mock_svc.get_release_detail.return_value = (release, release.artist, [])
                async with _App().run_test(size=(120, 40)) as pilot:
                    await asyncio.sleep(0.1)
                    await pilot.pause()
                    from textual.widgets import DataTable

                    count = (
                        pilot.app.query_one(ReleaseListSection)
                        .query_one(DataTable)
                        .row_count
                    )
                    await pilot.app.workers.wait_for_complete()
                    return count

        assert asyncio.run(_test()) == 1

    def test_release_selection_triggers_detail_load(self):
        release = _make_release(1)

        async def _test():
            with patch('pages.release.release_page.release_service') as mock_svc:
                mock_svc.get_all_releases.return_value = []
                mock_svc.get_release_detail.return_value = (release, release.artist, [])
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    page = pilot.app.query_one(ReleasePage)
                    page._load_release_detail(1)
                    await asyncio.sleep(0.1)
                    return (
                        mock_svc.get_release_detail.called,
                        mock_svc.get_release_detail.call_args,
                    )

        was_called, call_args = asyncio.run(_test())
        assert was_called
        assert call_args.args[0] == 1
