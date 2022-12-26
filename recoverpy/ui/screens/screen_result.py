from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.events import Event
from textual.screen import Screen
from textual.widgets import Label, Button, TextLog
from textual.reactive import reactive

from lib.helper import get_dd_output

from lib.helper import decode_result

from lib.helper import get_printable

from lib.saver import Saver


class ResultScreen(Screen):
    def __init__(self, *args, **kwargs):
        self._saver = Saver()
        self._partition = ""
        self._block_size = 0
        self._inode = 0
        self._inode_label = Label("", id="inode-label")
        self._block_count_label = Label("0 block selected", id="block-count")
        self._block_content = TextLog(markup=False, wrap=True)
        self._raw_block_content = None
        self._save_button = Button(label="Save", id="save-button", disabled=True)
        super().__init__(*args, **kwargs)

    def set(self, partition: str, block_size: int, inode: int) -> None:
        self._saver.reset()
        self._save_button.disabled = True
        self._partition = partition
        self._block_size = block_size
        self._inode = inode
        self.update_inode_label()
        self.update_block_content()
        self._block_count_label.update("0 block selected")

    def update_inode_label(self) -> None:
        self._inode_label.update(f"Result for inode {self._inode}")

    def update_block_content(self) -> None:
        self._block_content.clear()
        self._raw_block_content = decode_result(
            get_dd_output(self._partition, self._block_size, self._inode)
        )
        self._block_content.write(get_printable(self._raw_block_content))

    def compose(self) -> ComposeResult:

        yield Horizontal(self._inode_label, id="inode-label-container")
        yield Horizontal(self._block_content, id="block-content-container")
        yield Horizontal(
            self._block_count_label,
            id="block-count-container",
        )
        yield Horizontal(
            Button("Go back", id="go-back-button"), id="go-back-button-container"
        )
        yield Horizontal(
            Button("Previous", id="previous-button"),
            Button("Add block", id="add-block-button"),
            Button("Next", id="next-button"),
            id="block-buttons-container",
        )
        yield Horizontal(self._save_button, id="save-button-container")

    async def on_button_pressed(self, event: Event) -> None:
        button_id = event.sender.id
        if button_id == "go-back-button":
            self.app.pop_screen()
        elif button_id == "previous-button":
            self._inode -= 1
            self.update_inode_label()
            self.update_block_content()
        elif button_id == "add-block-button":
            self._saver.add(self._inode, self._raw_block_content)
            count = self._saver.get_selected_blocks_count()
            self._block_count_label.update(
                f"{count} block{'s' if count > 1 else ''} selected"
            )
            self._save_button.disabled = False
        elif button_id == "next-button":
            self._inode += 1
            self.update_inode_label()
            self.update_block_content()
        elif button_id == "save-button":
            self.app.get_screen("save").set_saver(self._saver)
            await self.app.push_screen("save")
