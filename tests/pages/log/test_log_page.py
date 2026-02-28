import asyncio
import logging
from unittest.mock import MagicMock

from textual.app import App, ComposeResult
from textual.widgets import Log

from pages.log.log_page import LogPane, WidgetLogHandler


class _App(App):
    def compose(self) -> ComposeResult:
        yield LogPane()


class TestWidgetLogHandler:
    def test_emit_buffers_when_no_widget(self):
        handler = WidgetLogHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        record = logging.LogRecord('test', logging.INFO, '', 0, 'hello', None, None)
        handler.emit(record)
        assert any('hello' in msg for msg in handler._buffer)

    def test_set_widget_flushes_buffer(self):
        handler = WidgetLogHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        record = logging.LogRecord('test', logging.INFO, '', 0, 'hello', None, None)
        handler.emit(record)

        widget = MagicMock(spec=Log)
        handler.set_widget(widget)

        widget.write_line.assert_called_once()
        assert handler._buffer == []

    def test_emit_writes_directly_when_widget_set(self):
        handler = WidgetLogHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        widget = MagicMock(spec=Log)
        handler._widget = widget

        record = logging.LogRecord('test', logging.INFO, '', 0, 'world', None, None)
        handler.emit(record)

        widget.write_line.assert_called_once()

    def test_buffer_empty_after_set_widget(self):
        handler = WidgetLogHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        for i in range(3):
            record = logging.LogRecord(
                'test', logging.INFO, '', 0, f'msg{i}', None, None
            )
            handler.emit(record)
        assert len(handler._buffer) == 3

        widget = MagicMock(spec=Log)
        handler.set_widget(widget)

        assert handler._buffer == []
        assert widget.write_line.call_count == 3


class TestLogPane:
    def test_compose_mounts_log_widget(self):
        async def _test():
            async with _App().run_test(size=(120, 40)) as pilot:
                return pilot.app.query_one('#log-widget', Log) is not None

        assert asyncio.run(_test())

    def test_on_unmount_removes_handler(self):
        handler_ref = None

        async def _test():
            nonlocal handler_ref
            async with _App().run_test(size=(120, 40)) as pilot:
                pane = pilot.app.query_one(LogPane)
                handler_ref = pane._handler
            # after context exit the app is stopped and on_unmount is called
            return handler_ref not in logging.getLogger().handlers

        assert asyncio.run(_test())
