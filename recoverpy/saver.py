from datetime import datetime

from recoverpy.logger import LOGGER as _LOGGER


class Saver:
    """Encapsulates all result saving related methods.

    Attributes:
        _save_path (str): Local path for search results saving.
        last_saved_file (str): Last saved file to inform user.
    """

    def __init__(self):
        """Constructor for Saver."""

        _save_path = None
        last_saved_file = None

    def set_save_path(self, path: str):
        """Set result save path based on config file

        Args:
            path (str): Local path for search results saving.
        """

        self._save_path = path

    def save_result(self, current_block: str, result: str):
        """Save a single result in a text file

        Args:
            current_block (str): Current partition block for file naming.
            result (str): Block content to be saved.
        """

        file_name = "{save_location}{time}-{block}".format(
            save_location=self._save_path,
            time=datetime.now().strftime("recoverpy-save-%Y-%m-%d-%H%M%S"),
            block=current_block,
        )

        with open(file_name, "w") as save_file:
            save_file.write(result)

        self.last_saved_file = file_name

        _LOGGER.write("info", f"Output saved in file {file_name}")

    def save_result_dict(self, results: dict):
        """Order a results dictionnary by block numbers and then save it in a text file.

        Args:
            results (dict): Blocks number and content to be ordered.
        """

        ordered_blocks = sorted(results)

        final_output = ""

        for key in ordered_blocks:
            final_output += results[key]
            final_output += "\n"

        date_time_name = datetime.now().strftime("recoverpy-save-%Y-%m-%d-%H%M%S")
        file_name = f"{self._save_path}{date_time_name}"

        with open(file_name, "w") as save_file:
            save_file.write(final_output)

        self.last_saved_file = file_name

        _LOGGER.write("info", f"Output saved in file {file_name}")


SAVER = Saver()
