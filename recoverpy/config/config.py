from pathlib import Path

from yaml import FullLoader, load

import recoverpy.utils.errors as _ERRORS
from recoverpy.utils.logger import LOGGER as _LOGGER
from recoverpy.utils.saver import SAVER as _SAVER


def parse_configuration():
    """Set logging and saving parameters based on yaml conf file.

    Raises:
        _ERRORS.NoSavePath: If config file save path is empty
        _ERRORS.InvalidSavePath: If config file save path is invalid
        _ERRORS.InvalidLogPath: If config file log path is invalid
    """
    project_path = Path(__file__).parent.absolute()

    with open(project_path / "config.yaml") as config_file:
        config = load(config_file, Loader=FullLoader)

    if config["save_directory"] == "":
        raise _ERRORS.NoSavePath
    if not Path(config["save_directory"]).is_dir():
        raise _ERRORS.InvalidSavePath

    _SAVER.set_save_path(config["save_directory"])

    if config["enable_logging"]:
        _LOGGER.enable_logging()
    else:
        return

    if config["log_directory"] == "":
        _LOGGER.disable_logging()
    elif not Path(config["log_directory"]).is_dir():
        raise _ERRORS.InvalidLogPath
    else:
        _LOGGER.set_log_file_path(config["log_directory"])
