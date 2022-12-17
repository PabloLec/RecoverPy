from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button, TextLog

from lib.search.static import get_dd_output

from lib.helper import decode_result

from lib.helper import get_printable


class ResultScreen(Screen):
    def __init__(self, *args, **kwargs):
        self._partition = ""
        self._block_size = 0
        self._inode = 0
        self._inode_label = Label("")
        self._block_content = TextLog(markup=False, wrap=True)
        super().__init__(*args, **kwargs)

    def set(self, partition: str,  block_size: int, inode: int) -> None:
        self._partition = partition
        self._block_size = block_size
        self._inode = inode
        self.update_inode_label()
        self.update_block_content()

    def update_inode_label(self) -> None:
        self._inode_label.update(f"Result for inode {self._inode}")

    def update_block_content(self) -> None:
        self._block_content.clear()
        self._block_content.write(get_printable(decode_result(get_dd_output(self._partition, self._block_size, self._inode))))

    def compose(self) -> ComposeResult:
        yield self._inode_label
        yield self._block_content
        yield Button("Go back", id="go-back-button")

    async def on_button_pressed(self) -> None:
        self.app.pop_screen()
