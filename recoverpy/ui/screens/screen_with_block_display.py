from subprocess import CalledProcessError
from typing import Optional

from py_cui import PyCUI
from py_cui.widgets import ScrollTextBlock

from recoverpy.lib.helper import decode_result, get_block_size
from recoverpy.lib.search.search_engine import SearchEngine
from recoverpy.lib.search.static import get_dd_output
from recoverpy.ui import strings
from recoverpy.ui.screens.screen import Screen


class MenuWithBlockDisplay(Screen):
    """Composition aimed class for menus needing methods to display partition
    blocks content.
    """

    def __init__(self, master: PyCUI):
        super().__init__(master)

        self.block_content_box: Optional[ScrollTextBlock] = None

        self.horizontal_char_limit: int = 0
        self.current_block: int = 0
        self.current_result: str = ""
        self.partition: str = ""
        self.search_engine = SearchEngine()

    def get_dd_result(self, block_number: int = None):
        if block_number is None:
            block_number = self.current_block

        try:
            dd_result: bytes = get_dd_output(
                partition=self.partition,
                block_size=get_block_size(self.partition),
                block_number=block_number,
            )

            self.current_result = decode_result(dd_result)
            self.current_block = block_number
        except CalledProcessError:
            self.master.show_error_popup(
                strings.title_generic_error,
                f"{strings.content_block_error} {str(self.current_block)}",
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

        self.block_content_box.set_text(formated_result)
        self.block_content_box.set_title(f"Block {self.current_block}")

    def display_previous_block(self):
        try:
            self.display_block(int(self.current_block) - 1)
        except ValueError:
            return

    def display_next_block(self):
        try:
            self.display_block(self.current_block + 1)
        except ValueError:
            return

    def display_block(self, block_number: int):
        if int(block_number) < 0:
            return

        self.get_dd_result(block_number=block_number)
        self.update_textbox()

    def update_horizontal_char_limit(self):
        text_box_dimensions: tuple = (
            self.block_content_box.get_cursor_limits_horizontal()
        )
        self.horizontal_char_limit: int = (
            text_box_dimensions[1] - text_box_dimensions[0]
        )
