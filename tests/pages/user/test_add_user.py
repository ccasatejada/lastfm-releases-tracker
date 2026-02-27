import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Button, Input

from pages.user.component.add_user import AddUserBar


class _App(App):
    def compose(self) -> ComposeResult:
        yield AddUserBar()


class TestAddUserBar:
    def test_compose_has_input_and_button(self):
        async def _test():
            async with _App().run_test(size=(80, 10)) as pilot:
                assert pilot.app.query_one('#username-input', Input)
                assert pilot.app.query_one('#ok-button', Button)

        asyncio.run(_test())

    def test_submit_via_button_posts_message(self):
        messages = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield AddUserBar()

            def on_add_user_bar_submitted(self, event: AddUserBar.Submitted):
                messages.append(event.username)

        async def _test():
            async with MockApp().run_test(size=(80, 10)) as pilot:
                pilot.app.query_one('#username-input', Input).value = 'Radiohead'
                pilot.app.query_one(AddUserBar).post_message(
                    Button.Pressed(pilot.app.query_one('#ok-button', Button))
                )
                await pilot.pause()

        asyncio.run(_test())
        assert messages == ['Radiohead']

    def test_empty_username_not_submitted(self):
        messages = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield AddUserBar()

            def on_add_user_bar_submitted(self, event: AddUserBar.Submitted):
                messages.append(event.username)

        async def _test():
            async with MockApp().run_test(size=(80, 10)) as pilot:
                pilot.app.query_one('#username-input', Input).value = ''
                pilot.app.query_one(AddUserBar).post_message(
                    Button.Pressed(pilot.app.query_one('#ok-button', Button))
                )
                await pilot.pause()

        asyncio.run(_test())
        assert messages == []

    def test_whitespace_only_not_submitted(self):
        messages = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield AddUserBar()

            def on_add_user_bar_submitted(self, event: AddUserBar.Submitted):
                messages.append(event.username)

        async def _test():
            async with MockApp().run_test(size=(80, 10)) as pilot:
                pilot.app.query_one('#username-input', Input).value = '   '
                pilot.app.query_one(AddUserBar).post_message(
                    Button.Pressed(pilot.app.query_one('#ok-button', Button))
                )
                await pilot.pause()

        asyncio.run(_test())
        assert messages == []

    def test_input_cleared_after_submit(self):
        async def _test():
            async with _App().run_test(size=(80, 10)) as pilot:
                inp = pilot.app.query_one('#username-input', Input)
                inp.value = 'Radiohead'
                pilot.app.query_one(AddUserBar).post_message(
                    Button.Pressed(pilot.app.query_one('#ok-button', Button))
                )
                await pilot.pause()
                return inp.value

        result = asyncio.run(_test())
        assert result == ''

    def test_submit_via_input_submitted_event(self):
        messages = []

        class MockApp(App):
            def compose(self) -> ComposeResult:
                yield AddUserBar()

            def on_add_user_bar_submitted(self, event: AddUserBar.Submitted):
                messages.append(event.username)

        async def _test():
            async with MockApp().run_test(size=(80, 10)) as pilot:
                inp = pilot.app.query_one('#username-input', Input)
                inp.value = 'Muse'
                pilot.app.query_one(AddUserBar).post_message(
                    Input.Submitted(inp, 'Muse')
                )
                await pilot.pause()

        asyncio.run(_test())
        assert messages == ['Muse']
