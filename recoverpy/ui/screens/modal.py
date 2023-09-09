from typing import Callable, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Grid, Horizontal
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, Label

from recoverpy.log.logger import log


class Modal(ModalScreen[None]):
    def __init__(self, name: str, message: str, callback: Optional[Callable] = None):  # type: ignore
        super().__init__(name=name)
        self._message_label = Label(message, id="modal-message")
        self._callback = callback or self.app.pop_screen
        self._is_error = "error" in name

    def compose(self) -> ComposeResult:
        grid_components: List[Widget] = [
            self._message_label,
            Horizontal(
                Button("OK", id="ok-button"),
                id="modal-button-container",
            ),
        ]

        if self._is_error:
            grid_components.insert(
                0, Label("An error occurred:", id="modal-error-label")
            )

        yield Grid(*grid_components, id="modal-container")
        log.info("Modal screen composed")

    def on_button_pressed(self) -> None:
        self._callback()


async def install_and_push_modal(
    app: App[None], name: str, message: str, callback: Optional[Callable] = None  # type: ignore
) -> None:
    modal = Modal(name, message=message, callback=callback)
    app.install_screen(modal, name)
    await app.push_screen(name)
