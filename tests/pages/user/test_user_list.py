import asyncio
from datetime import datetime

from textual.app import App, ComposeResult
from textual.coordinate import Coordinate
from textual.widgets import DataTable
from textual.widgets._data_table import CellKey, ColumnKey, RowKey

from model.model import AppUser
from pages.user.component.confirm_delete import ConfirmDeleteScreen
from pages.user.component.user_list import UserListSection


def _make_user(id: int, lastfm_username: str, username: str | None = None) -> AppUser:
    user = AppUser(id=id, lastfm_username=lastfm_username, username=username)
    user.created_at = datetime(2024, 1, 1)
    user.updated_at = datetime(2024, 1, 2)
    return user


class _App(App):
    def compose(self) -> ComposeResult:
        yield UserListSection()


class TestUserListSection:
    def test_columns_created_on_mount(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                table = pilot.app.query_one(DataTable)
                return [c.label.plain for c in table.columns.values()]

        cols = asyncio.run(_test())
        assert 'ID' in cols
        assert 'Last.fm' in cols
        assert 'Username' in cols
        assert 'Artists' in cols

    def test_add_user_adds_row(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(UserListSection)
                table = pilot.app.query_one(DataTable)
                section.add_user(_make_user(1, 'alice', 'Alice'), nb_artists=5)
                await pilot.pause()
                return table.row_count, table.get_row('user_1')

        count, row = asyncio.run(_test())
        assert count == 1
        assert row[0] == '1'
        assert row[1] == 'alice'
        assert row[2] == 'Alice'
        assert row[3] == '5'

    def test_add_user_default_nb_artists_zero(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(UserListSection)
                section.add_user(_make_user(1, 'alice'))
                await pilot.pause()
                return pilot.app.query_one(DataTable).get_row('user_1')

        row = asyncio.run(_test())
        assert row[3] == '0'

    def test_duplicate_user_not_added_twice(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(UserListSection)
                section.add_user(_make_user(1, 'alice'))
                section.add_user(_make_user(1, 'alice'))
                await pilot.pause()
                return pilot.app.query_one(DataTable).row_count

        count = asyncio.run(_test())
        assert count == 1

    def test_multiple_users_added(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(UserListSection)
                section.add_user(_make_user(1, 'alice'))
                section.add_user(_make_user(2, 'bob'))
                await pilot.pause()
                return pilot.app.query_one(DataTable).row_count

        count = asyncio.run(_test())
        assert count == 2

    def test_selected_message_posted_on_row_highlight(self):
        selected = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserListSection()

            def on_user_list_section_selected(self, event: UserListSection.Selected):
                selected.append((event.id_user, event.lastfm_username))

        async def _test():
            async with MockApp().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(UserListSection)
                section.add_user(_make_user(1, 'alice'))
                await pilot.pause()
                selected.clear()  # clear auto-highlight from add_user
                table = pilot.app.query_one(DataTable)
                row_key = RowKey('user_1')
                cell_key = CellKey(row_key, ColumnKey('col_id'))
                section.post_message(
                    DataTable.CellHighlighted(table, '1', Coordinate(0, 0), cell_key)
                )
                await pilot.pause()

        asyncio.run(_test())
        assert selected == [(1, 'alice')]


class TestDeleteCell:
    def test_cell_selected_on_delete_column_pushes_confirm_screen(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(UserListSection)
                section.add_user(_make_user(1, 'alice'))
                await pilot.pause()
                table = pilot.app.query_one(DataTable)
                row_key = RowKey('user_1')
                delete_cell_key = CellKey(row_key, ColumnKey('col_delete'))
                section.post_message(
                    DataTable.CellSelected(
                        table, '✕', Coordinate(0, 6), delete_cell_key
                    )
                )
                await pilot.pause()
                return pilot.app.screen

        screen = asyncio.run(_test())
        assert isinstance(screen, ConfirmDeleteScreen)

    def test_confirm_delete_removes_row_and_posts_delete_requested(self):
        deleted = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserListSection()

            def on_user_list_section_delete_requested(
                self, event: UserListSection.DeleteRequested
            ):
                deleted.append(event.id_user)

        async def _test():
            async with MockApp().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(UserListSection)
                section.add_user(_make_user(1, 'alice'))
                await pilot.pause()
                table = pilot.app.query_one(DataTable)
                row_key = RowKey('user_1')
                delete_cell_key = CellKey(row_key, ColumnKey('col_delete'))
                section.post_message(
                    DataTable.CellSelected(
                        table, '✕', Coordinate(0, 6), delete_cell_key
                    )
                )
                await pilot.pause()
                # confirm the deletion
                await pilot.click('#ok-btn')
                await pilot.pause()
                return pilot.app.query_one(DataTable).row_count

        row_count = asyncio.run(_test())
        assert row_count == 0
        assert deleted == [1]

    def test_cancel_delete_keeps_row(self):
        deleted = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserListSection()

            def on_user_list_section_delete_requested(self, event):
                deleted.append(event.id_user)

        async def _test():
            async with MockApp().run_test(size=(120, 40)) as pilot:
                section = pilot.app.query_one(UserListSection)
                section.add_user(_make_user(1, 'alice'))
                await pilot.pause()
                table = pilot.app.query_one(DataTable)
                row_key = RowKey('user_1')
                delete_cell_key = CellKey(row_key, ColumnKey('col_delete'))
                section.post_message(
                    DataTable.CellSelected(
                        table, '✕', Coordinate(0, 6), delete_cell_key
                    )
                )
                await pilot.pause()
                # cancel the deletion
                await pilot.click('#cancel-btn')
                await pilot.pause()
                return pilot.app.query_one(DataTable).row_count

        row_count = asyncio.run(_test())
        assert row_count == 1
        assert deleted == []
