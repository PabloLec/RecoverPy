from datetime import datetime

from recoverpy import logger as LOGGER

_SAVE_PATH = None


def set_save_path(path: str):
    """Sets result save path based on config file"""

    global _SAVE_PATH

    _SAVE_PATH = path


def save_result(current_block: str, result: str):
    """Saves a single result in a text file"""

    global _SAVE_PATH

    file_name = "{save_location}{time}-{block}".format(
        save_location=_SAVE_PATH,
        time=datetime.now().strftime("recoverpy-save-%Y-%m-%d-%H%M%S"),
        block=current_block,
    )

    with open(file_name, "w") as save_file:
        save_file.write(result)

    LOGGER.write("info", "Output saved in file {file_name}".format(file_name=file_name))


def save_result_dict(results: dict):
    """Orders a results dictionnary by block numbers and the saves it in a text file."""

    global _SAVE_PATH

    ordered_blocks = sorted(results)

    final_output = ""

    for key in ordered_blocks:
        final_output += results[key]
        final_output += "\n"

    file_name = "{save_location}{time}".format(
        save_location=_SAVE_PATH,
        time=datetime.now().strftime("recoverpy-save-%Y-%m-%d-%H%M%S"),
    )

    with open(file_name, "w") as save_file:
        save_file.write(final_output)
    LOGGER.write("info", "Output saved in file {file_name}".format(file_name=file_name))
