"""Screen used to select ressult save path."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Event
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button

from recoverpy.log.logger import log
from recoverpy.ui.widgets.directory_tree import DirectoryTree


class PathEditScreen(Screen[None]):
    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._directory_tree = DirectoryTree("/")

    class Confirm(Message):
        def __init__(self, selected_dir: str) -> None:
            super().__init__()
            self.selected_dir = selected_dir

    def compose(self) -> ComposeResult:
        yield self._directory_tree
        yield Horizontal(
            Button("Confirm", id="confirm-button"), id="path-edit-button-container"
        )
        log.info("path_edit - Path edit screen composed")

    async def on_button_pressed(self, event: Event) -> None:
        log.info("path_edit - Confirm button pressed")
        event.stop()
        self.app.get_screen("save").post_message(
            self.Confirm(self._directory_tree.selected_dir)
        )
        self.app.pop_screen()
