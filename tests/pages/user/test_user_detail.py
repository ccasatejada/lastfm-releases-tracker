import asyncio
from datetime import date, datetime

from textual.app import App, ComposeResult
from textual.widgets import Button, Input, Select

from model.model import AppUser, AppUserSettings
from pages.user.component.user_detail import UserDetailSection


class _App(App):
    def compose(self) -> ComposeResult:
        yield UserDetailSection()


def _make_user(id=1, lastfm_username='alice', username=None):
    user = AppUser(id=id, lastfm_username=lastfm_username, username=username)
    user.created_at = datetime(2024, 1, 1)
    user.updated_at = datetime(2024, 1, 1)
    return user


def _make_settings(min_scrobbles=1000, not_before=date(2023, 1, 1)):
    s = AppUserSettings()
    s.min_scrobbles = min_scrobbles
    s.releases_not_before = not_before
    return s


class TestShowUser:
    def test_hides_placeholder_and_reveals_content(self):
        async def _test():
            async with _App().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section.show_user('alice', _make_user(), None, None)
                await pilot.pause()
                placeholder_hidden = (
                    'hidden' in pilot.app.query_one('#detail-placeholder').classes
                )
                content_visible = (
                    'hidden' not in pilot.app.query_one('#detail-content').classes
                )
                return placeholder_hidden, content_visible

        placeholder_hidden, content_visible = asyncio.run(_test())
        assert placeholder_hidden
        assert content_visible

    def test_sets_inputs_from_settings(self):
        settings = _make_settings(min_scrobbles=500, not_before=date(2022, 6, 1))

        async def _test():
            async with _App().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section.show_user(
                    'alice', _make_user(username='Alice'), settings, 'mypassword'
                )
                await pilot.pause()
                return (
                    pilot.app.query_one('#username-input', Input).value,
                    pilot.app.query_one('#min-scrobbles-input', Input).value,
                    pilot.app.query_one('#releases-not-before-input', Input).value,
                    pilot.app.query_one('#password-input', Input).value,
                )

        username, min_s, rnb, password = asyncio.run(_test())
        assert username == 'Alice'
        assert min_s == '500'
        assert rnb == '2022-06-01'
        assert password == 'mypassword'

    def test_clears_inputs_when_no_settings(self):
        async def _test():
            async with _App().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section.show_user('alice', _make_user(), None, None)
                await pilot.pause()
                return (
                    pilot.app.query_one('#min-scrobbles-input', Input).value,
                    pilot.app.query_one('#releases-not-before-input', Input).value,
                )

        min_s, rnb = asyncio.run(_test())
        assert min_s == ''
        assert rnb == ''

    def test_populates_artist_select(self):
        async def _test():
            async with _App().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section.show_user(
                    'alice',
                    _make_user(),
                    None,
                    None,
                    artists=[(1, 'Radiohead'), (2, 'Muse')],
                )
                await pilot.pause()
                select = pilot.app.query_one('#artist-select', Select)
                return len(select._options)

        # Select includes a blank/prompt entry in addition to user options
        count = asyncio.run(_test())
        assert count >= 2


class TestSetFetching:
    def test_true_disables_button(self):
        async def _test():
            async with _App().run_test(size=(160, 60)) as pilot:
                pilot.app.query_one(UserDetailSection).set_fetching(True)
                await pilot.pause()
                btn = pilot.app.query_one('#fetch-artist-button', Button)
                return btn.disabled, str(btn.label)

        disabled, label = asyncio.run(_test())
        assert disabled
        assert 'Fetching' in label

    def test_false_restores_button(self):
        async def _test():
            async with _App().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section.set_fetching(True)
                await pilot.pause()
                section.set_fetching(False)
                await pilot.pause()
                btn = pilot.app.query_one('#fetch-artist-button', Button)
                return btn.disabled, str(btn.label)

        disabled, label = asyncio.run(_test())
        assert not disabled
        assert 'artists' in label.lower()

    def test_set_fetching_releases_true(self):
        async def _test():
            async with _App().run_test(size=(160, 60)) as pilot:
                pilot.app.query_one(UserDetailSection).set_fetching_releases(True)
                await pilot.pause()
                return pilot.app.query_one('#fetch-release-button', Button).disabled

        assert asyncio.run(_test())

    def test_set_fetching_releases_false(self):
        async def _test():
            async with _App().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section.set_fetching_releases(True)
                await pilot.pause()
                section.set_fetching_releases(False)
                await pilot.pause()
                return pilot.app.query_one('#fetch-release-button', Button).disabled

        assert not asyncio.run(_test())

    def test_set_fetching_all_releases_true(self):
        async def _test():
            async with _App().run_test(size=(160, 60)) as pilot:
                pilot.app.query_one(UserDetailSection).set_fetching_all_releases(True)
                await pilot.pause()
                return pilot.app.query_one(
                    '#fetch-all-releases-button', Button
                ).disabled

        assert asyncio.run(_test())

    def test_set_fetching_all_releases_false(self):
        async def _test():
            async with _App().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section.set_fetching_all_releases(True)
                await pilot.pause()
                section.set_fetching_all_releases(False)
                await pilot.pause()
                return pilot.app.query_one(
                    '#fetch-all-releases-button', Button
                ).disabled

        assert not asyncio.run(_test())


class TestSubmitSettings:
    def test_valid_inputs_posts_settings_changed(self):
        received = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserDetailSection()

            def on_user_detail_section_settings_changed(
                self, event: UserDetailSection.SettingsChanged
            ):
                received.append(event)

        async def _test():
            async with MockApp().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section._current_id_user = 1
                pilot.app.query_one('#username-input', Input).value = 'alice'
                pilot.app.query_one('#min-scrobbles-input', Input).value = '500'
                pilot.app.query_one(
                    '#releases-not-before-input', Input
                ).value = '2023-01-01'
                section._submit_settings()
                await pilot.pause()

        asyncio.run(_test())
        assert len(received) == 1
        assert received[0].min_scrobbles == 500
        assert received[0].releases_not_before == date(2023, 1, 1)
        assert received[0].username == 'alice'

    def test_empty_min_uses_default_1000(self):
        received = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserDetailSection()

            def on_user_detail_section_settings_changed(
                self, event: UserDetailSection.SettingsChanged
            ):
                received.append(event)

        async def _test():
            async with MockApp().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section._current_id_user = 1
                section._submit_settings()
                await pilot.pause()

        asyncio.run(_test())
        assert received[0].min_scrobbles == 1000

    def test_invalid_min_scrobbles_does_not_post(self):
        received = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserDetailSection()

            def on_user_detail_section_settings_changed(self, event):
                received.append(event)

        async def _test():
            async with MockApp().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section._current_id_user = 1
                pilot.app.query_one(
                    '#min-scrobbles-input', Input
                ).value = 'not-a-number'
                section._submit_settings()
                await pilot.pause()

        asyncio.run(_test())
        assert len(received) == 0

    def test_invalid_date_does_not_post(self):
        received = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserDetailSection()

            def on_user_detail_section_settings_changed(self, event):
                received.append(event)

        async def _test():
            async with MockApp().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section._current_id_user = 1
                pilot.app.query_one(
                    '#releases-not-before-input', Input
                ).value = 'not-a-date'
                section._submit_settings()
                await pilot.pause()

        asyncio.run(_test())
        assert len(received) == 0


class TestRequestFetchArtists:
    def test_no_password_does_not_post(self):
        received = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserDetailSection()

            def on_user_detail_section_fetch_requested(self, event):
                received.append(event)

        async def _test():
            async with MockApp().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section._lastfm_username = 'alice'
                section._request_fetch_artists()
                await pilot.pause()

        asyncio.run(_test())
        assert len(received) == 0

    def test_with_password_posts_fetch_requested(self):
        received = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserDetailSection()

            def on_user_detail_section_fetch_requested(
                self, event: UserDetailSection.FetchRequested
            ):
                received.append(event)

        async def _test():
            async with MockApp().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section._lastfm_username = 'alice'
                pilot.app.query_one('#password-input', Input).value = 'mypassword'
                section._request_fetch_artists()
                await pilot.pause()

        asyncio.run(_test())
        assert len(received) == 1
        assert received[0].lastfm_username == 'alice'
        assert received[0].lastfm_password == 'mypassword'


class TestRequestFetchAllReleases:
    def test_no_password_does_not_post(self):
        received = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserDetailSection()

            def on_user_detail_section_fetch_all_releases_requested(self, event):
                received.append(event)

        async def _test():
            async with MockApp().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section._lastfm_username = 'alice'
                section._request_fetch_all_releases()
                await pilot.pause()

        asyncio.run(_test())
        assert len(received) == 0

    def test_with_password_posts_fetch_all_releases_requested(self):
        received = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserDetailSection()

            def on_user_detail_section_fetch_all_releases_requested(
                self, event: UserDetailSection.FetchAllReleasesRequested
            ):
                received.append(event)

        async def _test():
            async with MockApp().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section._lastfm_username = 'alice'
                pilot.app.query_one('#password-input', Input).value = 'pass'
                section._request_fetch_all_releases()
                await pilot.pause()

        asyncio.run(_test())
        assert len(received) == 1
        assert received[0].lastfm_username == 'alice'


class TestRequestFetchReleases:
    def test_no_password_does_not_post(self):
        received = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserDetailSection()

            def on_user_detail_section_fetch_releases_requested(self, event):
                received.append(event)

        async def _test():
            async with MockApp().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section._lastfm_username = 'alice'
                section._request_fetch_releases()
                await pilot.pause()

        asyncio.run(_test())
        assert len(received) == 0

    def test_no_artist_selected_does_not_post(self):
        received = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield UserDetailSection()

            def on_user_detail_section_fetch_releases_requested(self, event):
                received.append(event)

        async def _test():
            async with MockApp().run_test(size=(160, 60)) as pilot:
                section = pilot.app.query_one(UserDetailSection)
                section._lastfm_username = 'alice'
                pilot.app.query_one('#password-input', Input).value = 'pass'
                # no artist selected — Select.BLANK
                section._request_fetch_releases()
                await pilot.pause()

        asyncio.run(_test())
        assert len(received) == 0
