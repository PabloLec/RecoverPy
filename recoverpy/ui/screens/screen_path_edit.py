"""Screen used to select ressult save path."""

from textual._types import MessageTarget
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Event
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button

from recoverpy.ui.widgets.directory_tree import DirectoryTree


class PathEditScreen(Screen):
    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        self._directory_tree = DirectoryTree("/")
        super().__init__(*args, **kwargs)

    class Confirm(Message):
        def __init__(self, sender: MessageTarget, selected_dir: str) -> None:
            self.selected_dir = selected_dir
            super().__init__(sender)

    def compose(self) -> ComposeResult:
        yield self._directory_tree
        yield Horizontal(
            Button("Confirm", id="confirm-button"), id="path-edit-button-container"
        )

    async def on_button_pressed(self, event: Event) -> None:
        event.stop()
        await self.app.get_screen("save").post_message(
            self.Confirm(self, self._directory_tree.selected_dir)
        )
        self.app.pop_screen()
