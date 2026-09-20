from __future__ import annotations

import logging

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Log

# todo put it to some log conf file - with LogPane custom widget
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
# logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)
# logging.getLogger("sqlalchemy.orm").setLevel(logging.INFO)

DEFAULT_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'


class WidgetLogHandler(logging.Handler):
    """Routes Python log records into a Textual Log widget.

    Before the widget is ready, records are buffered in memory.
    Call ``set_widget`` once the Log widget is mounted to flush
    the buffer and start writing directly.
    """

    def __init__(self) -> None:
        super().__init__()
        self._widget: Log | None = None
        self._buffer: list[str] = []

    def set_widget(self, widget: Log) -> None:
        self._widget = widget
        for msg in self._buffer:
            self._widget.write_line(msg)
        self._buffer.clear()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            if self._widget is not None:
                self._widget.write_line(msg)
            else:
                self._buffer.append(msg)
        except Exception:
            self.handleError(record)


class LogPane(Vertical):
    """Drop-in Textual widget that captures Python logging into a Log widget.

    Usage — just mount it anywhere in your app:

        with TabPane("Logs"):
            yield LogPane()

    The handler is attached to the root logger immediately at construction
    time so that log records emitted during ``compose()`` of sibling widgets
    are captured (buffered until the Log widget is mounted).
    """

    def __init__(
        self,
        *,
        level: int = logging.DEBUG,
        log_format: str = DEFAULT_FORMAT,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)

        self._handler = WidgetLogHandler()
        self._handler.setFormatter(logging.Formatter(log_format))

        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(level)
        root_logger.addHandler(self._handler)

    def compose(self) -> ComposeResult:
        yield Log(auto_scroll=True, id='log-widget')

    def on_mount(self) -> None:
        self._handler.set_widget(self.query_one(Log))

    def on_unmount(self) -> None:
        logging.getLogger().removeHandler(self._handler)
