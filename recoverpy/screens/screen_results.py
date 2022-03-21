from py_cui import PyCUI

from recoverpy import screen_handler as screen_handler
from recoverpy.utils.logger import LOGGER as LOGGER
from recoverpy.utils.saver import SAVER as SAVER
from recoverpy.screens.screen_with_block_display import MenuWithBlockDisplay


class ResultsScreen(MenuWithBlockDisplay):
    """ResultsScreen let the user navigate through partition blocks and save results.

    Args:
        _BLOCK_DISPLAY_MENU (MenuWithBlockDisplay): Composition to inherit block display
        methods.

    Attributes:
        saved_blocks_dict (dict): Used to store block numbers associated with their text
            contents. Will be used to save it in a file.
        current_block (int): Partition block number currently displayed.
    """

    def __init__(self, master: PyCUI, partition: str, initial_block: int):
        """Initialize ResultsScreen.

        Args:
            master (PyCUI): PyCUI main object for UI.
            partition (str): System partition to search.
            initial_block (int): Initial partition block number that will be displayed.
        """
        super().__init__(master)

        self.master = master
        self.partition = partition

        LOGGER.write("info", "Starting 'ResultsScreen' CUI window")

        self.saved_blocks_dict = {}

        self.current_block = initial_block

        self.create_ui_content()
        # Display initial block at opening
        self.display_block(self.current_block)

    def create_ui_content(self):
        """Handle the creation of the UI elements."""
        self.previous_button = self.master.add_button(
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

        self.next_button = self.master.add_button(
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

        self.result_content_box = self.master.add_text_block(
            "Block content:", 0, 1, row_span=9, column_span=8, padx=1, pady=0
        )
        self.result_content_box.set_title(f"Block {self.current_block}")

        self.add_result_button = self.master.add_button(
            "Add current block to file",
            9,
            0,
            row_span=1,
            column_span=5,
            padx=1,
            pady=0,
            command=self.add_block_to_file,
        )
        self.add_result_button.set_color(6)

        self.save_file_button = self.master.add_button(
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

        self.go_back_button = self.master.add_button(
            "Go back to previous screen",
            9,
            8,
            row_span=1,
            column_span=2,
            padx=1,
            pady=0,
            command=screen_handler.SCREENS_HANDLER.results_go_back,
        )
        self.go_back_button.set_color(2)

    def add_block_to_file(self):
        """Store currently displayed result in a dict to save it later."""
        if self.current_block in self.saved_blocks_dict:
            return

        self.master.show_message_popup("", "Result added to file")
        self.saved_blocks_dict[self.current_block] = self.current_result
        LOGGER.write(
            "debug",
            f"Stored block {self.current_block} for future save",
        )

    def save_file(self):
        """Bundle results saving and popup message."""
        len_results = len(self.saved_blocks_dict)

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
