from py_cui import PyCUI
from py_cui.widgets import Button, ScrollTextBlock

from recoverpy.ui import handler as handler
from recoverpy.ui.screen_with_block_display import MenuWithBlockDisplay
from recoverpy.utils.logger import LOGGER as LOGGER
from recoverpy.utils.saver import SAVER as SAVER


class BlockScreen(MenuWithBlockDisplay):
    """Navigate through found partition blocks and save results."""

    def __init__(self, master: PyCUI, partition: str, initial_block: int):
        super().__init__(master)

        self.partition: str = partition
        self.saved_blocks_dict: dict = {}
        self.current_block: int = initial_block

        self.create_ui_content()
        self.display_block(self.current_block)

    def create_ui_content(self):
        self.previous_button: Button = self.master.add_button(
            "<",
            3,
            0,
            row_span=3,
            column_span=1,
            padx=1,
            pady=0,
            command=self.display_previous_block,
        )
        self.previous_button.set_color(1)

        self.next_button: Button = self.master.add_button(
            ">",
            3,
            9,
            row_span=3,
            column_span=1,
            padx=1,
            pady=0,
            command=self.display_next_block,
        )
        self.next_button.set_color(1)

        self.blockcontent_box: ScrollTextBlock = self.master.add_text_block(
            "Block content:", 0, 1, row_span=9, column_span=8, padx=1, pady=0
        )
        self.blockcontent_box.set_title(f"Block {self.current_block}")

        self.add_blockbutton: Button = self.master.add_button(
            "Add current block to file",
            9,
            0,
            row_span=1,
            column_span=5,
            padx=1,
            pady=0,
            command=self.add_block_to_file,
        )
        self.add_blockbutton.set_color(6)

        self.save_file_button: Button = self.master.add_button(
            "Save file",
            9,
            5,
            row_span=1,
            column_span=3,
            padx=1,
            pady=0,
            command=self.save_file,
        )
        self.save_file_button.set_color(4)

        self.go_back_button: Button = self.master.add_button(
            "Go back to previous screen",
            9,
            8,
            row_span=1,
            column_span=2,
            padx=1,
            pady=0,
            command=handler.SCREENS_HANDLER.go_back,
        )
        self.go_back_button.set_color(2)

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
