import os
import logging
import yaml

import recoverpy.errors as ERRORS
import recoverpy.window_handler as WINDOW_HANDLER
import recoverpy.logger as LOGGER
import recoverpy.saver as SAVER

_LOGGER = logging.getLogger(__name__)


def parse_configuration():
    """Sets logging and saving parameters based on yaml conf file."""

    with open(os.path.join(os.path.dirname(__file__), "config.yaml")) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    if config["save_directory"] == "":
        raise ERRORS.NoSavePath
    elif not os.path.isdir(config["save_directory"]):
        raise ERRORS.InvalidSavePath
    else:
        SAVER.set_save_path(config["save_directory"])

    if config["enable_logging"]:
        LOGGER.enable_logging()
    else:
        return

    if config["log_directory"] == "":
        LOGGER.disable_logging()
    elif not os.path.isdir(config["log_directory"]):
        raise ERRORS.InvalidLogPath
    else:
        LOGGER.set_log_file_path(config["log_directory"])


def main():
    parse_configuration()

    WINDOW_HANDLER.open_parameters_menu()
