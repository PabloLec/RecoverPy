from subprocess import CalledProcessError
from typing import Optional

from py_cui import PyCUI

from recoverpy.ui.screen import Screen
from recoverpy.utils.helper import decode_result, get_block_size
from recoverpy.utils.logger import LOGGER
from recoverpy.utils.search import SearchEngine


class MenuWithBlockDisplay(Screen):
    """Composition aimed class for menus needing methods to display partition
    blocks content.
    """

    def __init__(self, master: PyCUI):
        super().__init__(master)

        self.horizontal_char_limit: int = 0

        self.current_block: Optional[str] = None
        self.current_result: Optional[str] = None
        self.partition: Optional[str] = None

    def get_dd_result(self, block_number: str = None):
        if block_number is None:
            block_number = self.current_block

        LOGGER.write(
            "debug",
            f"Getting 'dd' output for block {str(self.current_block)}",
        )

        try:
            dd_result: bytes = SearchEngine.get_dd_output(
                partition=self.partition,
                block_size=get_block_size(self.partition),
                block_number=block_number,
            )

            self.current_result = decode_result(dd_result)
            self.current_block = block_number

            LOGGER.write("debug", "dd command successful")
        except CalledProcessError:
            self.master.show_error_popup(
                "Mmmmhhh...",
                f"Error while opening block {str(self.current_block)}",
            )
            LOGGER.write(
                "error",
                f"Error while opening block {str(self.current_block)}",
            )

    def update_textbox(self):
        self.update_horizontal_char_limit()

        # Format raw result to fit in the text box
        blocklines: list = [
            str(self.current_result)[i : i + self.horizontal_char_limit]
            for i in range(
                0,
                len(str(self.current_result)) + self.horizontal_char_limit,
                self.horizontal_char_limit,
            )
        ]
        formated_result: str = "\n".join(blocklines)

        # Fix for embedded null character
        formated_result = formated_result.replace(chr(0), "")

        self.blockcontent_box.set_text(formated_result)
        self.blockcontent_box.set_title(f"Block {self.current_block}")

        LOGGER.write("debug", f"Textbox updated with block {self.current_block}")

    def display_previous_block(self):
        try:
            self.display_block(str(int(self.current_block) - 1))
        except ValueError:
            LOGGER.write("error", f"Cannot display block {self.current_block} - 1")
            return

    def display_next_block(self):
        try:
            self.display_block(str(int(self.current_block) + 1))
        except ValueError:
            LOGGER.write("error", f"Cannot display block {self.current_block} + 1")
            return

    def display_block(self, block_number: str):
        if int(block_number) < 0:
            return

        self.get_dd_result(block_number=block_number)
        self.update_textbox()

    def update_horizontal_char_limit(self):
        text_box_dimensions: tuple = (
            self.blockcontent_box.get_cursor_limits_horizontal()
        )
        self.horizontal_char_limit: int = (
            text_box_dimensions[1] - text_box_dimensions[0]
        )
        LOGGER.write(
            "debug",
            f"Textbox char limit set to {self.horizontal_char_limit}",
        )
