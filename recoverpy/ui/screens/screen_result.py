from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button


class ResultScreen(Screen):
    _inode_label: Label

    def __init__(self, *args, **kwargs):
        self._inode = 0
        self._inode_label = Label("")
        super().__init__(*args, **kwargs)

    def set_inode(self, inode: int) -> None:
        self._inode = inode
        self.update_inode_label()

    def update_inode_label(self) -> None:
        self._inode_label.update(f"Result for inode {self._inode}")

    def compose(self) -> ComposeResult:
        yield self._inode_label
        yield Button("Go back", id="go-back-button")

    async def on_button_pressed(self) -> None:
        self.app.pop_screen()
