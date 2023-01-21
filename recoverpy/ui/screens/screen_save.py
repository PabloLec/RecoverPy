"""Screen used to confirm save."""
from typing import Optional

from textual._types import MessageTarget
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Label

from recoverpy.lib.saver import Saver
from recoverpy.ui.screens.screen_path_edit import PathEditScreen


class SaveScreen(Screen):
    class Saved(Message):
        def __init__(self, sender: MessageTarget, save_path: str) -> None:
            self.save_path = save_path
            super().__init__(sender)

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        self._saver: Optional[Saver] = None
        self._save_path_label = Label("", id="save-path-label")
        super().__init__(*args, **kwargs)

    def set_saver(self, saver: Saver) -> None:
        self._saver = saver
        self._set_save_path()

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Current save path:", id="save-path-title-label"),
            self._save_path_label,
            id="save-path-container",
        )
        yield Horizontal(
            Button("Go back", id="go-back-button"),
            Button("Edit save path", id="edit-save-path-button"),
            Button("Save", id="save-button"),
            id="action-buttons-container",
        )

    def _set_save_path(self) -> None:
        if self._saver:
            self._save_path_label.update(str(self._saver.save_path))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "go-back-button":
            self.app.pop_screen()
        elif button_id == "edit-save-path-button":
            await self.app.push_screen("path_edit")
        elif button_id == "save-button" and self._saver:
            self._saver.save()
            self.app.pop_screen()
            if self._saver.last_saved_file:
                await self.app.post_message(
                    self.Saved(
                        self, str(self._saver.save_path / self._saver.last_saved_file)
                    )
                )

    async def on_path_edit_screen_confirm(self, event: PathEditScreen.Confirm) -> None:
        if self._saver:
            self._saver.update_save_path(event.selected_dir)
            self._set_save_path()
