from datetime import datetime

from recoverpy import logger as LOGGER

_SAVE_PATH = None
_LAST_SAVED_FILE = None


def set_save_path(path: str):
    """Sets result save path based on config file"""

    global _SAVE_PATH

    _SAVE_PATH = path


def save_result(current_block: str, result: str):
    """Saves a single result in a text file"""

    global _SAVE_PATH
    global _LAST_SAVED_FILE

    file_name = "{save_location}{time}-{block}".format(
        save_location=_SAVE_PATH,
        time=datetime.now().strftime("recoverpy-save-%Y-%m-%d-%H%M%S"),
        block=current_block,
    )

    with open(file_name, "w") as save_file:
        save_file.write(result)

    _LAST_SAVED_FILE = file_name

    LOGGER.write("info", f"Output saved in file {file_name}")


def save_result_dict(results: dict):
    """Orders a results dictionnary by block numbers and the saves it in a text file."""

    global _SAVE_PATH
    global _LAST_SAVED_FILE

    ordered_blocks = sorted(results)

    final_output = ""

    for key in ordered_blocks:
        final_output += results[key]
        final_output += "\n"

    file_name = f"{_SAVE_PATH}{datetime.now().strftime('recoverpy-save-%Y-%m-%d-%H%M%S')}"

    with open(file_name, "w") as save_file:
        save_file.write(final_output)

    _LAST_SAVED_FILE = file_name

    LOGGER.write("info", f"Output saved in file {file_name}")
