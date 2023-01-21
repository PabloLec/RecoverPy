"""Screen displaying dd results."""
from subprocess import CalledProcessError
from typing import Optional, cast

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Label, TextLog

from recoverpy.lib.helper import decode_result, get_dd_output, get_printable
from recoverpy.lib.saver import Saver
from recoverpy.ui.screens.screen_save import SaveScreen


class ResultScreen(Screen):
    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        self._saver = Saver()
        self._partition = ""
        self._block_size = 0
        self._inode = 0
        self._inode_label = Label("", id="inode-label")
        self._block_count_label = Label("0 block selected", id="block-count")
        self._block_content = TextLog(markup=False, wrap=True)
        self._raw_block_content: Optional[str] = None
        self._save_button = Button(label="Save", id="save-button", disabled=True)
        super().__init__(*args, **kwargs)

    def set(self, partition: str, block_size: int, inode: int) -> None:
        self._saver.reset()
        self._save_button.disabled = True
        self._partition = partition
        self._block_size = block_size
        self._inode = inode
        self._update()
        self._block_count_label.update("0 block selected")

    def _update(self) -> None:
        self._update_inode_label()
        try:
            self._update_block_content()
        except CalledProcessError:
            self._block_content.write(f"Cannot read block {self._inode}")

    def _update_inode_label(self) -> None:
        self._inode_label.update(f"Result for inode {self._inode}")

    def _update_block_content(self) -> None:
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

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "go-back-button":
            self.app.pop_screen()
        elif button_id == "previous-button" and self._inode > 0:
            self._inode -= 1
            self._update()
        elif button_id == "add-block-button" and self._raw_block_content:
            self._saver.add(self._inode, self._raw_block_content)
            count = self._saver.get_selected_blocks_count()
            self._block_count_label.update(
                f"{count} block{'s' if count > 1 else ''} selected"
            )
            self._save_button.disabled = False
        elif button_id == "next-button":
            self._inode += 1
            self._update()
        elif button_id == "save-button":
            cast(SaveScreen, self.app.get_screen("save")).set_saver(self._saver)
            await self.app.push_screen("save")
