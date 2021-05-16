from subprocess import check_output

from recoverpy import logger as LOGGER


class MenuWithBlockDisplay:
    """Composition aimed class for menus needing methods to display partition
    blocks content.

    Attributes:
        master (py_cui.PyCUI): PyCUI constructor.
        horizontal_char_limit (int): Number of chars that can fit horizontally in
            the left hand result box.
        current_block (int): Partition block number currently displayed.
        current_result (int): Block text content found with dd command.
        result_content_box (PyCUI.TextBox): TextBox in which dd command result
            will be displayed.
        partition (str): System partition selected by user for search.
    """

    def __init__(self):
        """Constructor for MenuWithBlockDisplay"""

        self.master = None

        self.horizontal_char_limit = 0

        self.current_block = 0
        self.current_result = None

        self.result_content_box = None
        self.partition = None

    def get_dd_result(self, block: str = None):
        """Stores a 'dd' command result in current_result var

        Args:
            block (str, optional): Partition block number. Defaults to None.
        """

        if block is None:
            block = self.current_block

        LOGGER.write(
            "debug",
            "Getting 'dd' output for block {current_block}".format(current_block=str(self.current_block)),
        )

        try:
            dd_result = check_output(
                [
                    "dd",
                    "if={partition}".format(partition=self.partition),
                    "count=1",
                    "status=none",
                    "skip={block}".format(block=block),
                ]
            )
            # Try/Catch to decode raw result in utf-8
            try:
                self.current_result = dd_result.decode("utf-8")
            except:
                self.current_result = str(dd_result)
            self.current_block = block

            LOGGER.write("debug", "dd command successful")
        except:
            self.master.show_error_popup(
                "ERROR",
                "Error while opening block {current_block}".format(current_block=str(self.current_block)),
            )
            LOGGER.write(
                "error",
                "Error while opening block {current_block}".format(current_block=str(self.current_block)),
            )

    def update_textbox(self):
        """Formats 'dd' result by breaking lines with char_limit var.
        Then displays it in lefthand texbox.
        """
        self.update_char_limit()

        # Format raw result to display it in the text box
        result_lines = [
            str(self.current_result)[i : i + self.horizontal_char_limit]
            for i in range(0, len(str(self.current_result)), self.horizontal_char_limit)
        ]
        formated_result = "\n".join(result_lines)

        self.result_content_box.set_text(formated_result)
        self.result_content_box.set_title("Block {current_block}".format(current_block=str(self.current_block)))

        LOGGER.write(
            "debug",
            "Textbox updated with block {current_block}".format(current_block=str(self.current_block)),
        )

    def display_previous_block(self):
        """Function to display block n-1 in textbox."""

        try:
            self.display_block(str(int(self.current_block) - 1))
        except ValueError:
            LOGGER.write(
                "error",
                "Cannot display block {block} - 1".format(block=self.current_block),
            )
            return

    def display_next_block(self):
        """Function to display block n+1 in textbox."""

        try:
            self.display_block(str(int(self.current_block) + 1))
        except ValueError:
            LOGGER.write(
                "error",
                "Cannot display block {block} + 1".format(block=self.current_block),
            )
            return

    def display_block(self, block: str):
        """Function to display given block number in textbox.

        Args:
            block (str): Partition block number.
        """

        self.get_dd_result(block=block)
        self.update_textbox()

    def update_char_limit(self):
        """Update horizontal character limit for textbox depending on terminal size."""

        text_box_dimensions = self.result_content_box.get_cursor_limits_horizontal()
        self.horizontal_char_limit = text_box_dimensions[1] - text_box_dimensions[0]
        LOGGER.write(
            "debug",
            "Textbox char limit set to {char_limit}".format(char_limit=self.horizontal_char_limit),
        )
