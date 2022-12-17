from asyncio import Event

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen

from lib.saver import Saver
from textual.widgets import Label, Button

from ui.screens.screen_path_edit import PathEditScreen


class SaveScreen(Screen):
    def __init__(self, *args, **kwargs):
        self._saver = None
        self._save_path_label = Label("", id="save-path-label")
        super().__init__(*args, **kwargs)

    def set_saver(self, saver: Saver) -> None:
        self._saver = saver
        self._set_save_path()

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Current save path:", id="save-path-title-label"),
            self._save_path_label,
            id="save-path-container")
        yield Horizontal(
            Button("Go back", id="go-back-button"),
            Button("Edit save path", id="edit-save-path-button"),
            Button("Save", id="save-button"),
            id="action-buttons-container"
        )

    def _set_save_path(self):
        self._save_path_label.update(str(self._saver.save_path))

    async def on_button_pressed(self, event: Event) -> None:
        button_id = event.sender.id
        if button_id == "go-back-button":
            self.app.pop_screen()
        elif button_id == "edit-save-path-button":
            await self.app.push_screen("path_edit")
        elif button_id == "save-button":
            self._saver.save()
            self.app.pop_screen()

    async def on_path_edit_screen_confirm(self, event: PathEditScreen.Confirm) -> None:
        print(event.selected_dir)
        self._saver.update_save_path(event.selected_dir)
        self._set_save_path()
