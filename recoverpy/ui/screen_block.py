from py_cui import PyCUI

from recoverpy.lib.saver import SAVER as SAVER
from recoverpy.ui import strings as STRINGS
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

        self.master.show_message_popup(
            STRINGS.title_empty, STRINGS.content_result_added
        )
        self.saved_blocks_dict[self.current_block] = self.current_result

    def save_file(self):
        len_results: int = len(self.saved_blocks_dict)

        if len_results == 0:
            self.master.show_message_popup(
                STRINGS.title_empty, STRINGS.content_no_result
            )
            return

        SAVER.save_result_dict(self.saved_blocks_dict)

        if len_results == 1:
            self.master.show_message_popup(
                STRINGS.title_empty,
                f"{STRINGS.one_block_saved} {SAVER.last_saved_file}",
            )
        else:
            self.master.show_message_popup(
                STRINGS.title_empty,
                f"{len_results} {STRINGS.multiple_blocks_saved} "
                f"{SAVER.last_saved_file}",
            )
