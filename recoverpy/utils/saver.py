from datetime import datetime

from recoverpy.utils.logger import LOGGER


class Saver:
    """Encapsulates all result saving related methods.

    Attributes:
        _save_path (str): Local path for search results saving.
        last_saved_file (str): Last saved file to inform user.
    """

    def __init__(self):
        """Initialize Saver."""
        self._save_path = None
        self.last_saved_file = None

    def set_save_path(self, path: str):
        """Set result save path based on config file.

        Args:
            path (str): Local path for search results saving
        """
        self._save_path = path

    def save_result(self, current_block: str, result: str):
        """Save a single result in a text file.

        Args:
            current_block (str): Current partition block for file naming
            result (str): Block content to be saved
        """
        time_format = datetime.now().strftime("recoverpy-save-%Y-%m-%d-%H%M%S")
        file_name = f"{self._save_path}{time_format}-{current_block}"

        self.write_to_file(file_name=file_name, content=result)

    def save_result_dict(self, results: dict):
        """Order a results dictionnary by block numbers and then save it in a text file.

        Args:
            results (dict): Blocks number and content to be ordered
        """
        ordered_blocks = sorted(results)

        final_output = ""

        for key in ordered_blocks:
            final_output += results[key]
            final_output += "\n"

        date_time_name = datetime.now().strftime("recoverpy-save-%Y-%m-%d-%H%M%S")
        file_name = f"{self._save_path}{date_time_name}"

        self.write_to_file(file_name=file_name, content=final_output)

    def write_to_file(self, file_name: str, content: str):
        """Write content provided save file.

        Args:
            file_name (str): Save file name
            content (str): File content to be written
        """
        with open(file_name, "w") as save_file:
            save_file.write(content)

        self.last_saved_file = file_name

        LOGGER.write("info", f"Output saved in file {file_name}")


SAVER = Saver()
