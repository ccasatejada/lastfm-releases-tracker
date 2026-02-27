import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Button

from pages.user.component.confirm_delete import ConfirmDeleteScreen


def _make_app(dismiss_results: list):
    class _App(App):
        def compose(self) -> ComposeResult:
            return iter([])

        def on_mount(self):
            self.push_screen(ConfirmDeleteScreen(), lambda r: dismiss_results.append(r))

    return _App


class TestConfirmDeleteScreen:
    def test_ok_button_dismisses_true(self):
        results = []

        async def _test():
            async with _make_app(results)().run_test(size=(80, 24)) as pilot:
                await pilot.pause()
                pilot.app.screen.query_one('#ok-btn', Button).press()
                await pilot.pause()

        asyncio.run(_test())
        assert results == [True]

    def test_cancel_button_dismisses_false(self):
        results = []

        async def _test():
            async with _make_app(results)().run_test(size=(80, 24)) as pilot:
                await pilot.pause()
                pilot.app.screen.query_one('#cancel-btn', Button).press()
                await pilot.pause()

        asyncio.run(_test())
        assert results == [False]

    def test_escape_key_dismisses_false(self):
        results = []

        async def _test():
            async with _make_app(results)().run_test(size=(80, 24)) as pilot:
                await pilot.pause()
                await pilot.press('escape')
                await pilot.pause()

        asyncio.run(_test())
        assert results == [False]

    def test_compose_has_question_label(self):
        async def _test():
            async with _make_app([])().run_test(size=(80, 24)) as pilot:
                await pilot.pause()
                from textual.widgets import Label

                label = pilot.app.screen.query_one('#confirm-question', Label)
                return label.content

        result = asyncio.run(_test())
        assert 'sure' in result.lower()
