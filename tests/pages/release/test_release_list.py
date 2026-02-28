import asyncio
from datetime import date

from textual.app import App, ComposeResult
from textual.widgets import DataTable

from pages.release.component.release_list import ReleaseListSection


def _make_row(
    release_id,
    artist='Radiohead',
    title='OK Computer',
    release_date=date(1997, 6, 16),
    length=3180,
    nb_tracks=12,
    url='https://example.com',
):
    return (release_id, artist, title, release_date, length, nb_tracks, url)


class _App(App):
    def compose(self) -> ComposeResult:
        yield ReleaseListSection()


class TestReleaseListSection:
    def test_columns_created_on_mount(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                table = pilot.app.query_one(DataTable)
                return [c.label.plain for c in table.columns.values()]

        cols = asyncio.run(_test())
        assert 'Date' in cols
        assert 'Artist' in cols
        assert 'Title' in cols
        assert 'Length' in cols
        assert 'Tracks' in cols
        assert 'URL' in cols

    def test_load_releases_adds_rows(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseListSection)
                section.load_releases([_make_row(1), _make_row(2)])
                await pilot.pause()
                return pilot.app.query_one(DataTable).row_count

        assert asyncio.run(_test()) == 2

    def test_load_empty_list_shows_no_rows(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseListSection)
                section.load_releases([])
                await pilot.pause()
                return pilot.app.query_one(DataTable).row_count

        assert asyncio.run(_test()) == 0

    def test_load_clears_previous_rows(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseListSection)
                section.load_releases([_make_row(1), _make_row(2)])
                await pilot.pause()
                section.load_releases([_make_row(3)])
                await pilot.pause()
                return pilot.app.query_one(DataTable).row_count

        assert asyncio.run(_test()) == 1

    def test_selected_message_posted_on_row_highlight(self):
        selected = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield ReleaseListSection()

            def on_release_list_section_selected(
                self, event: ReleaseListSection.Selected
            ):
                selected.append(event.release_id)

        async def _test():
            async with MockApp().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseListSection)
                section.load_releases([_make_row(42)])
                await pilot.pause()
                selected.clear()  # clear auto-highlight from load
                table = pilot.app.query_one(DataTable)
                row_key = list(table.rows.keys())[0]
                section.post_message(DataTable.RowHighlighted(table, 0, row_key))
                await pilot.pause()

        asyncio.run(_test())
        assert selected == [42]

    def test_row_highlighted_with_no_key_does_not_raise(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ReleaseListSection)
                table = pilot.app.query_one(DataTable)
                # Simulate a highlight event with no row_key
                from textual.widgets._data_table import RowKey

                section.post_message(DataTable.RowHighlighted(table, 0, RowKey()))
                await pilot.pause()

        asyncio.run(_test())  # should not raise
