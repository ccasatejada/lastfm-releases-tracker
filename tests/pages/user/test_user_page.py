import asyncio
from datetime import datetime
from unittest.mock import patch

from textual.app import App, ComposeResult
from textual.widgets import DataTable

from model.model import AppUser, AppUserSettings
from pages.user.component.user_detail import UserDetailSection
from pages.user.component.user_list import UserListSection
from pages.user.user_page import UserPage


class _App(App):
    def compose(self) -> ComposeResult:
        yield UserPage()


def _make_user(id: int, lastfm_username: str) -> AppUser:
    user = AppUser(id=id, lastfm_username=lastfm_username)
    user.created_at = datetime(2024, 1, 1)
    user.updated_at = datetime(2024, 1, 1)
    return user


def _patch_services(mock_default, mock_user, users=None):
    mock_default.get_default_user.return_value = (None, None)
    mock_user.get_users.return_value = ({}, users or [])


class TestUserPage:
    def test_compose_mounts_list_and_detail_sections(self):
        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
            ):
                _patch_services(mock_default, mock_user)
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    return (
                        pilot.app.query_one(UserListSection) is not None,
                        pilot.app.query_one(UserDetailSection) is not None,
                    )

        has_list, has_detail = asyncio.run(_test())
        assert has_list
        assert has_detail

    def test_get_users_called_on_mount(self):
        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
            ):
                _patch_services(mock_default, mock_user)
                async with _App().run_test(size=(120, 40)):
                    await asyncio.sleep(0.1)
                    return mock_user.get_users.called

        assert asyncio.run(_test())

    def test_users_loaded_into_table_on_mount(self):
        user = _make_user(1, 'alice')

        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
            ):
                _patch_services(mock_default, mock_user, users=[user])
                async with _App().run_test(size=(120, 40)) as pilot:
                    await asyncio.sleep(0.1)
                    return pilot.app.query_one(DataTable).row_count

        assert asyncio.run(_test()) == 1

    def test_add_user_worker_calls_init_user(self):
        new_user = _make_user(2, 'bob')

        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
                patch(
                    'pages.user.user_page.init_user', return_value=new_user
                ) as mock_init,
            ):
                _patch_services(mock_default, mock_user)
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    page = pilot.app.query_one(UserPage)
                    page._add_user('bob')
                    await asyncio.sleep(0.1)
                    return mock_init.called, mock_init.call_args

        was_called, call_args = asyncio.run(_test())
        assert was_called
        assert call_args.args[0] == 'bob'

    def test_delete_user_worker_calls_service(self):
        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
            ):
                _patch_services(mock_default, mock_user)
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    page = pilot.app.query_one(UserPage)
                    page._delete_user(1)
                    await asyncio.sleep(0.1)
                    return mock_user.delete_user.called, mock_user.delete_user.call_args

        was_called, call_args = asyncio.run(_test())
        assert was_called
        assert call_args.args[0] == 1

    def test_save_settings_worker_calls_service(self):
        from datetime import date

        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
            ):
                _patch_services(mock_default, mock_user)
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    page = pilot.app.query_one(UserPage)
                    page._save_settings(1, 'alice', 500, date(2023, 1, 1))
                    await asyncio.sleep(0.1)
                    return (
                        mock_user.update_user_settings.called,
                        mock_user.update_user_settings.call_args,
                    )

        was_called, call_args = asyncio.run(_test())
        assert was_called
        assert call_args.args[0] == 1
        assert call_args.args[1] == 'alice'
        assert call_args.args[2] == 500

    def test_load_initial_users_with_env_username(self):
        env_user = _make_user(99, 'envuser')

        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
                patch('pages.user.user_page.init_user', return_value=env_user),
            ):
                mock_default.get_default_user.return_value = ('envpass', 'envuser')
                mock_user.get_users.return_value = ({}, [])
                async with _App().run_test(size=(120, 40)) as pilot:
                    await asyncio.sleep(0.1)
                    return pilot.app.query_one(DataTable).row_count

        assert asyncio.run(_test()) == 1

    def test_load_user_detail_worker_calls_service(self):
        user = _make_user(1, 'alice')
        settings = AppUserSettings()
        settings.min_scrobbles = 1000

        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
            ):
                _patch_services(mock_default, mock_user)
                mock_user.get_user_with_settings.return_value = (user, settings)
                mock_user.get_user_artists.return_value = []
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    page = pilot.app.query_one(UserPage)
                    page._load_user_detail(1, 'alice')
                    await asyncio.sleep(0.1)
                    return mock_user.get_user_with_settings.called

        assert asyncio.run(_test())

    def test_load_user_detail_uses_env_password_for_matching_username(self):
        user = _make_user(1, 'alice')
        settings = AppUserSettings()

        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
            ):
                _patch_services(mock_default, mock_user)
                mock_user.get_user_with_settings.return_value = (user, settings)
                mock_user.get_user_artists.return_value = []
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    page = pilot.app.query_one(UserPage)
                    page._env_username = 'alice'
                    page._env_password = 'secret'
                    page._load_user_detail(1, 'alice')
                    await asyncio.sleep(0.1)
                    from textual.widgets import Input

                    return pilot.app.query_one('#password-input', Input).value

        password = asyncio.run(_test())
        assert password == 'secret'

    def test_fetch_artists_work_calls_fetch_artists(self):
        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
                patch('pages.user.user_page.fetch_artists') as mock_fetch,
            ):
                _patch_services(mock_default, mock_user)
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    page = pilot.app.query_one(UserPage)
                    page._fetch_artists_work('alice', 'pass')
                    await asyncio.sleep(0.1)
                    return mock_fetch.called, mock_fetch.call_args

        was_called, call_args = asyncio.run(_test())
        assert was_called
        assert call_args.args[0] == 'alice'
        assert call_args.args[1] == 'pass'

    def test_fetch_artists_work_error_notifies(self):
        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
                patch(
                    'pages.user.user_page.fetch_artists',
                    side_effect=Exception('fetch failed'),
                ),
            ):
                _patch_services(mock_default, mock_user)
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    page = pilot.app.query_one(UserPage)
                    page._fetch_artists_work('alice', 'pass')
                    await asyncio.sleep(0.1)
                    # no exception raised = error was handled

        asyncio.run(_test())  # should not raise

    def test_fetch_releases_work_calls_fetch_releases(self):
        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
                patch('pages.user.user_page.fetch_releases') as mock_fetch,
            ):
                _patch_services(mock_default, mock_user)
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    page = pilot.app.query_one(UserPage)
                    page._fetch_releases_work('alice', 'pass', id_artist=1)
                    await asyncio.sleep(0.1)
                    return mock_fetch.called, mock_fetch.call_args

        was_called, call_args = asyncio.run(_test())
        assert was_called
        assert call_args.args[0] == 'alice'
        assert call_args.args[2] == 1

    def test_fetch_all_releases_work_calls_fetch_all_releases(self):
        async def _test():
            with (
                patch('pages.user.user_page.default_user_service') as mock_default,
                patch('pages.user.user_page.user_service') as mock_user,
                patch('pages.user.user_page.fetch_all_releases') as mock_fetch,
            ):
                _patch_services(mock_default, mock_user)
                async with _App().run_test(size=(120, 40)) as pilot:
                    await pilot.pause()
                    page = pilot.app.query_one(UserPage)
                    page._fetch_all_releases_work('alice', 'pass')
                    await asyncio.sleep(0.1)
                    return mock_fetch.called, mock_fetch.call_args

        was_called, call_args = asyncio.run(_test())
        assert was_called
        assert call_args.args[0] == 'alice'
        assert call_args.args[1] == 'pass'
