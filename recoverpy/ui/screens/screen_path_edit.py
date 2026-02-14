"""Screen used to select result save path."""

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Label

from recoverpy.log.logger import log
from recoverpy.ui.widgets.folder_only_directory_tree import FolderOnlyDirectoryTree


class PathEditScreen(Screen[None]):
    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._selected_dir = "/"
        self._directory_tree: DirectoryTree | None = None
        self._selected_dir_label = Label("", id="selected-dir-label")

    class Confirm(Message):
        def __init__(self, selected_dir: str) -> None:
            super().__init__()
            self.selected_dir = selected_dir

    def compose(self) -> ComposeResult:
        self._directory_tree = FolderOnlyDirectoryTree("/", id="path-directory-tree")
        yield self._directory_tree
        yield self._selected_dir_label
        yield Horizontal(
            Button("Confirm", id="confirm-button", variant="success"),
            id="path-edit-button-container",
        )
        log.info("path_edit - Path edit screen composed")

    def on_mount(self) -> None:
        self._selected_dir_label.update(f"Selected directory: {self._selected_dir}")
        if self._directory_tree:
            self._directory_tree.focus()

    async def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        event.stop()
        self._selected_dir = str(event.path)
        self._selected_dir_label.update(f"Selected directory: {self._selected_dir}")

    async def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        event.stop()
        self.notify("Only directories can be selected.", severity="warning")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "confirm-button":
            return
        log.info("path_edit - Confirm button pressed")
        event.stop()
        self.app.get_screen("save").post_message(self.Confirm(self._selected_dir))
        self.app.pop_screen()
