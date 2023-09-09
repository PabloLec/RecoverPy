"""Screen displaying dd results."""
from subprocess import CalledProcessError
from typing import Optional, cast

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Label, RichLog

from recoverpy.lib.helper import decode_result, get_dd_output, get_printable
from recoverpy.lib.saver import Saver
from recoverpy.log.logger import log
from recoverpy.ui.screens.screen_save import SaveScreen


class ResultScreen(Screen[None]):
    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self._saver = Saver()
        self._partition = ""
        self._block_size = 0
        self._inode = 0
        self._inode_label = Label("", id="inode-label")
        self._block_count_label = Label("0 block selected", id="block-count")
        self._block_content = RichLog(markup=False, wrap=True)
        self._raw_block_content: Optional[str] = None
        self._save_button = Button(label="Save", id="save-button", disabled=True)

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
        log.debug("result - Result screen composed")

    def set(self, partition: str, block_size: int, inode: int) -> None:
        self._saver.reset()
        self._save_button.disabled = True
        self._partition = partition
        self._block_size = block_size
        self._inode = inode
        self._update_ui()
        self._block_count_label.update("0 block selected")

    def _update_ui(self) -> None:
        self._update_inode_label()
        self._update_block_content()

    def _update_inode_label(self) -> None:
        self._inode_label.update(f"Result for inode {self._inode}")

    def _update_block_content(self) -> None:
        self._block_content.clear()
        try:
            self._raw_block_content = decode_result(
                get_dd_output(self._partition, self._block_size, self._inode)
            )
            self._block_content.write(get_printable(self._raw_block_content))
            log.info("Block content updated")
        except CalledProcessError:
            log.error(f"Cannot read block {self._inode}")
            self._block_content.write(f"Cannot read block {self._inode}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        actions = {
            "go-back-button": self._handle_go_back,
            "previous-button": self._handle_previous,
            "add-block-button": self._handle_add_block,
            "next-button": self._handle_next,
            "save-button": self._handle_save,
        }

        if button_id in actions:
            await actions[button_id]()

    async def _handle_go_back(self) -> None:
        log.info("Go back button pressed")
        self.app.pop_screen()

    async def _handle_previous(self) -> None:
        if self._inode > 0:
            log.info("Previous button pressed")
            self._inode -= 1
            self._update_ui()

    async def _handle_add_block(self) -> None:
        if self._raw_block_content:
            log.info("Add block button pressed")
            self._saver.add(self._inode, self._raw_block_content)
            count = self._saver.get_selected_blocks_count()
            self._block_count_label.update(
                f"{count} block{'s' if count > 1 else ''} selected"
            )
            self._save_button.disabled = False

    async def _handle_next(self) -> None:
        log.info("Next button pressed")
        self._inode += 1
        self._update_ui()

    async def _handle_save(self) -> None:
        log.info("Save button pressed")
        cast(SaveScreen, self.app.get_screen("save")).set_saver(self._saver)
        await self.app.push_screen("save")
