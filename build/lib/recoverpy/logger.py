from datetime import datetime

import logging

_LOG_FILE_PATH = None
_LOG_ENABLED = False
_LOGGER = None


def enable_logging():
    """Enable logging based on config file."""

    global _LOG_ENABLED

    _LOG_ENABLED = True


def disable_logging():
    """Disable logging based on config file."""

    global _LOG_ENABLED

    _LOG_ENABLED = False


def set_log_file_path(path):
    """Sets result save path based on config file"""

    global _LOG_FILE_PATH

    _LOG_FILE_PATH = path
    start_logging()


def start_logging():
    """Main logging function, initiates and configures the logger object."""

    global _LOG_FILE_PATH
    global _LOGGER

    time = datetime.now().strftime("%Y-%m-%d-%H%M%S")

    log_file_name = "{path}recoverpy-{time}.log".format(path=_LOG_FILE_PATH, time=time)

    _LOGGER = logging.getLogger("main")
    _LOGGER.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.DEBUG)

    _LOGGER.addHandler(file_handler)


def write(log_type, text: str):
    """Uses logger object to write to file."""

    global _LOG_ENABLED
    global _LOGGER

    if not _LOG_ENABLED:
        return

    if log_type == "debug":
        _LOGGER.debug(text)
    elif log_type == "info":
        _LOGGER.info(text)
    elif log_type == "warning":
        _LOGGER.warning(text)
    elif log_type == "error":
        _LOGGER.error(text)
    elif log_type == "critical":
        _LOGGER.critical(text)