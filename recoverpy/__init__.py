from os import environ
from pathlib import Path
from logging import getLogger
from yaml import load, FullLoader

import recoverpy.errors as ERRORS
from recoverpy.views_handler import VIEWS_HANDLER as _VIEWS_HANDLER
from recoverpy.logger import LOGGER as _LOGGER
from recoverpy.saver import SAVER as _SAVER

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
    if not Path(config["save_directory"]).is_dir():
        raise ERRORS.InvalidSavePath

    _SAVER.set_save_path(config["save_directory"])

    if config["enable_logging"]:
        _LOGGER.enable_logging()
    else:
        return

    if config["log_directory"] == "":
        _LOGGER.disable_logging()
    elif not Path(config["log_directory"]).is_dir():
        raise ERRORS.InvalidLogPath
    else:
        _LOGGER.set_log_file_path(config["log_directory"])


def main():
    """Setup configuration and start UI."""

    verify_terminal_conf()
    parse_configuration()

    _VIEWS_HANDLER.open_view_parameters()
