from py_cui import PyCUI

from recoverpy.lib.logger import LOGGER as LOGGER
from recoverpy.lib.saver import SAVER as SAVER
from recoverpy.ui.screen_with_block_display import MenuWithBlockDisplay


class BlockScreen(MenuWithBlockDisplay):
    """Navigate through found partition blocks and save results."""

    def __init__(self, master: PyCUI, partition: str, initial_block: int):
        super().__init__(master)

        self.partition: str = partition
        self.saved_blocks_dict: dict = {}
        self.current_block: int = initial_block

        self.create_ui_content()
        self.display_block(self.current_block)

    def add_block_to_file(self):
        if self.current_block in self.saved_blocks_dict:
            return

        self.master.show_message_popup("", "Result added to file")
        self.saved_blocks_dict[self.current_block] = self.current_result
        LOGGER.write(
            "debug",
            f"Stored block {self.current_block} for future save",
        )

    def save_file(self):
        len_results: int = len(self.saved_blocks_dict)

        if len_results == 0:
            self.master.show_message_popup("", "No result to save yet")
            return

        SAVER.save_result_dict(self.saved_blocks_dict)

        if len_results == 1:
            self.master.show_message_popup(
                "",
                f"Block saved in {SAVER.last_saved_file}",
            )
        else:
            self.master.show_message_popup(
                "",
                f"{len_results} blocks saved in {SAVER.last_saved_file}",
            )
