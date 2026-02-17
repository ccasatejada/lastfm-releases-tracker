from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

import logging
logger = logging.getLogger(__name__)

class ReleasePage(Vertical):

    def compose(self) -> ComposeResult:
        logger.info("Loading Release Page")
        yield Static('Releases — coming soon')
