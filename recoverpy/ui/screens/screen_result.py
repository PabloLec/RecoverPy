from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Event
from textual.screen import Screen
from textual.widgets import Label, Button, TextLog

from lib.helper import get_dd_output

from lib.helper import decode_result

from lib.helper import get_printable

from lib.saver import Saver


class ResultScreen(Screen):
    def __init__(self, *args, **kwargs):
        self.saver = Saver()
        self._partition = ""
        self._block_size = 0
        self._inode = 0
        self._inode_label = Label("", id="inode-label")
        self._block_content = TextLog(markup=False, wrap=True)
        self._raw_block_content = None
        super().__init__(*args, **kwargs)

    def set(self, partition: str, block_size: int, inode: int) -> None:
        self.saver.reset()
        self._partition = partition
        self._block_size = block_size
        self._inode = inode
        self.update_inode_label()
        self.update_block_content()
        self.saver.add(self._inode, self._raw_block_content)

    def update_inode_label(self) -> None:
        self._inode_label.update(f"Result for inode {self._inode}")

    def update_block_content(self) -> None:
        self._block_content.clear()
        self._raw_block_content = decode_result(get_dd_output(self._partition, self._block_size, self._inode))
        self._block_content.write(get_printable(self._raw_block_content))

    def compose(self) -> ComposeResult:
        yield Horizontal(self._inode_label, id="inode-label-container")
        yield Horizontal(self._block_content, id="block-content-container")
        yield Horizontal(Button("Go back", id="go-back-button"), id="go-back-button-container")
        yield Horizontal(
            Button("Previous", id="previous-button"),
            Button("Add block", id="add-block-button"),
            Button("Next", id="next-button"),
            id="block-buttons-container"
        )
        yield Horizontal(
            Button("Save", id="save-button"),
            id="save-button-container"
        )

    async def on_button_pressed(self, event: Event) -> None:
        button_id = event.sender.id
        if button_id == "go-back-button":
            self.app.pop_screen()
        elif button_id == "previous-button":
            self._inode -= 1
            self.update_inode_label()
            self.update_block_content()
        elif button_id == "add-block-button":
            self.saver.add(self._inode, self._raw_block_content)
        elif button_id == "next-button":
            self._inode += 1
            self.update_inode_label()
            self.update_block_content()
        elif button_id == "save-button":
            self.saver.save()
