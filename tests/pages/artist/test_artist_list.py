import asyncio
from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import DataTable

from pages.artist.component.artist_list import ArtistListSection


class _App(App):
    def compose(self) -> ComposeResult:
        yield ArtistListSection()


class TestArtistListSection:
    def test_columns_created_on_mount(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                table = pilot.app.query_one(DataTable)
                return [c.label.plain for c in table.columns.values()]

        cols = asyncio.run(_test())
        assert 'ID' in cols
        assert 'Artist name' in cols
        assert 'Releases' in cols
        assert 'Users' in cols

    def test_load_artists_adds_rows(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ArtistListSection)
                rows = [
                    (1, 'Radiohead', 10, 3, datetime(2024, 1, 1), datetime(2024, 1, 2)),
                    (2, 'Muse', 5, 1, datetime(2024, 2, 1), datetime(2024, 2, 2)),
                ]
                section.load_artists(rows)
                await pilot.pause()
                return pilot.app.query_one(DataTable).row_count

        count = asyncio.run(_test())
        assert count == 2

    def test_load_empty_list(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ArtistListSection)
                section.load_artists([])
                await pilot.pause()
                return pilot.app.query_one(DataTable).row_count

        count = asyncio.run(_test())
        assert count == 0

    def test_selected_message_posted_on_row_highlight(self):
        selected = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield ArtistListSection()

            def on_artist_list_section_selected(
                self, event: ArtistListSection.Selected
            ):
                selected.append(event.artist_id)

        async def _test():
            async with MockApp().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(ArtistListSection)
                section.load_artists(
                    [
                        (
                            1,
                            'Radiohead',
                            10,
                            3,
                            datetime(2024, 1, 1),
                            datetime(2024, 1, 2),
                        )
                    ]
                )
                await pilot.pause()
                selected.clear()  # clear auto-highlight from load_artists
                table = pilot.app.query_one(DataTable)
                row_key = list(table.rows.keys())[0]
                section.post_message(DataTable.RowHighlighted(table, 0, row_key))
                await pilot.pause()

        asyncio.run(_test())
        assert selected == [1]
