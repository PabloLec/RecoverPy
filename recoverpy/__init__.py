from subprocess import PIPE, Popen, check_output
from threading import Thread
from queue import Queue, Empty
from shlex import quote
from datetime import datetime

import os
import time
import re
import logging
import yaml
import py_cui

import recoverpy.errors as ERRORS
import recoverpy.window_handler as WINDOW_HANDLER
import recoverpy.logger as LOGGER
import recoverpy.saver as SAVER
import recoverpy.menu_with_block_display as BLOCK_DISPLAY_MENU
import recoverpy.search_menu as SEARCH_MENU
import recoverpy.block_menu as BLOCK_MENU

_LOGGER = logging.getLogger(__name__)


def parse_configuration():
    """Sets logging and saving paramters based on yaml conf file."""

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
