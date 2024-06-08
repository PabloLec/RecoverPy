"""Screen used to confirm save."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Label

from recoverpy.lib.saver import Saver
from recoverpy.log.logger import log
from recoverpy.ui.screens.screen_path_edit import PathEditScreen


class SaveScreen(Screen[None]):
    class Saved(Message):
        def __init__(self, save_path: str) -> None:
            super().__init__()
            self.save_path = save_path

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._saver: Optional[Saver] = None
        self._save_path_label = Label("", id="save-path-label")

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
        log.debug("save - Save screen composed")

    def set_saver(self, saver: Saver) -> None:
        self._saver = saver
        self._update_save_path_label()

    def _update_save_path_label(self) -> None:
        if self._saver:
            self._save_path_label.update(str(self._saver.save_path))
            log.info(f"save - Save path set to {self._saver.save_path}")
        else:
            log.error("save - Saver not set for path setting")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "go-back-button": self._handle_go_back,
            "edit-save-path-button": self._handle_edit_save_path,
            "save-button": self._handle_save,
        }

        button_id = event.button.id
        if button_id in actions:
            await actions[button_id]()

    async def _handle_go_back(self) -> None:
        log.info("save - Go back button pressed")
        self.app.pop_screen()

    async def _handle_edit_save_path(self) -> None:
        log.info("save - Edit save path button pressed")
        await self.app.push_screen("path_edit")

    async def _handle_save(self) -> None:
        if self._saver:
            log.info("save - Save button pressed")
            self._saver.save_results()
            self.app.pop_screen()
            if self._saver.last_saved_file:
                self.app.post_message(
                    self.Saved(str(self._saver.save_path / self._saver.last_saved_file))
                )
        else:
            log.error("save - Saver not set for saving")

    async def on_path_edit_screen_confirm(self, event: PathEditScreen.Confirm) -> None:
        if self._saver:
            self._saver.set_save_path(event.selected_dir)
            self._update_save_path_label()
        else:
            log.error("save - Saver not set for path editing")
