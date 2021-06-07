from os import environ
from pathlib import Path
from logging import getLogger
from yaml import load, FullLoader

import recoverpy.errors as ERRORS
import recoverpy.views_handler as VIEWS_HANDLER
import recoverpy.logger as LOGGER
import recoverpy.saver as SAVER

getLogger(__name__)


def verify_terminal_conf():
    """Fix for outdated terminals not compatible with curses."""

    term = environ["TERM"]

    if term != "xterm-256color":
        environ["TERM"] = "xterm-256color"


def parse_configuration():
    """Sets logging and saving parameters based on yaml conf file."""

    project_path = Path(__file__).parent.absolute()

    with open(project_path / "config.yaml") as config_file:
        config = load(config_file, Loader=FullLoader)

    if config["save_directory"] == "":
        raise ERRORS.NoSavePath
    elif not Path(config["save_directory"]).is_dir():
        raise ERRORS.InvalidSavePath
    else:
        SAVER.set_save_path(config["save_directory"])

    if config["enable_logging"]:
        LOGGER.enable_logging()
    else:
        return

    if config["log_directory"] == "":
        LOGGER.disable_logging()
    elif not Path(config["log_directory"]).is_dir():
        raise ERRORS.InvalidLogPath
    else:
        LOGGER.set_log_file_path(config["log_directory"])


def main():
    verify_terminal_conf()
    parse_configuration()

    VIEWS_HANDLER.open_view_parameters()
