"""Screen used to display a modal dialog."""

from textual.app import ComposeResult
from textual.containers import Grid, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Label


class ModalScreen(Screen):
    _message_label = Label("", id="modal-message")

    def set_message(self, message: str) -> None:
        self._message_label.update(message)

    def compose(self) -> ComposeResult:
        yield Grid(
            self._message_label,
            Horizontal(
                Button("OK", id="ok-button"),
                id="modal-button-container",
            ),
            id="modal-container",
        )

    def on_button_pressed(self) -> None:
        self.app.pop_screen()
