from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button


class ResultScreen(Screen):
    _inode: int

    def set_inode(self, inode: int) -> None:
        self._inode = inode

    def compose(self) -> ComposeResult:
        yield Label(f"Result for inode {self._inode}")
        yield Button("Go back", id="go-back-button")

    async def on_button_pressed(self) -> None:
        self.app.pop_screen()
