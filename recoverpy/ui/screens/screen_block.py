from py_cui import PyCUI

from recoverpy.lib.saver import Saver
from recoverpy.ui import strings
from recoverpy.ui.screens.screen_with_block_display import MenuWithBlockDisplay


class BlockScreen(MenuWithBlockDisplay):
    """Navigate through found partition blocks and save results."""

    def __init__(self, master: PyCUI, partition: str, initial_block: int):
        super().__init__(master)

        self.partition: str = partition
        self.saved_blocks_dict: dict = {}
        self.current_block: int = initial_block
        self.saver: Saver = Saver()

        self.create_ui_content()
        self.display_block(self.current_block)

    def add_block_to_file(self):
        if self.current_block in self.saved_blocks_dict:
            return

        self.master.show_message_popup(
            strings.title_empty, strings.content_result_added
        )
        self.saved_blocks_dict[self.current_block] = self.current_result

    def save_file(self):
        len_results: int = len(self.saved_blocks_dict)

        if len_results == 0:
            self.master.show_message_popup(
                strings.title_empty, strings.content_no_result
            )
            return

        self.saver.save_result_dict(self.saved_blocks_dict)

        if len_results == 1:
            self.master.show_message_popup(
                strings.title_empty,
                f"{strings.one_block_saved} {self.saver.last_saved_file}",
            )
        else:
            self.master.show_message_popup(
                strings.title_empty,
                f"{len_results} {strings.multiple_blocks_saved} "
                f"{self.saver.last_saved_file}",
            )
