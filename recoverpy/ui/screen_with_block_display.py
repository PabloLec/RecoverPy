from subprocess import CalledProcessError, check_output
from py_cui import PyCUI

from recoverpy.ui.screen import Screen
from recoverpy.utils.logger import LOGGER


class MenuWithBlockDisplay(Screen):
    """Composition aimed class for menus needing methods to display partition
    blocks content.
    """

    def __init__(self, master: PyCUI):
        super().__init__(master)

        self.horizontal_char_limit = 0

        self.current_block = None
        self.current_result = None

        self.blockcontent_box = None
        self.partition = None

    def get_dd_result(self, block: str = None):
        if block is None:
            block = self.current_block

        LOGGER.write(
            "debug",
            f"Getting 'dd' output for block {str(self.current_block)}",
        )

        try:
            dd_result = check_output(
                [
                    "dd",
                    f"if={self.partition}",
                    "count=1",
                    "status=none",
                    f"skip={block}",
                ]
            )
            # Try/Catch to decode raw result in utf-8
            try:
                self.current_result = dd_result.decode("utf-8")
            except UnicodeDecodeError:
                self.current_result = str(dd_result)
            self.current_block = block

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

        # Format raw result to display it in the text box
        blocklines = [
            str(self.current_result)[i : i + self.horizontal_char_limit]
            for i in range(0, len(str(self.current_result)), self.horizontal_char_limit)
        ]
        formated_result = "\n".join(blocklines)

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

    def display_block(self, block: str):
        if int(block) < 0:
            return

        self.get_dd_result(block=block)
        self.update_textbox()

    def update_horizontal_char_limit(self):
        text_box_dimensions = self.blockcontent_box.get_cursor_limits_horizontal()
        self.horizontal_char_limit = text_box_dimensions[1] - text_box_dimensions[0]
        LOGGER.write(
            "debug",
            f"Textbox char limit set to {self.horizontal_char_limit}",
        )
