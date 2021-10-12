from pathlib import Path

from yaml import FullLoader, dump, load

from recoverpy.utils import errors
from recoverpy.utils.logger import LOGGER
from recoverpy.utils.saver import SAVER

_CONFIG_DIR = Path(__file__).parent.absolute()


def path_is_valid(path: str):
    path = Path(path)
    try:
        if not path.is_dir():
            return False
    except PermissionError:
        return False

    return True


def write_config(save_path: str, log_path: str, enable_logging: bool):
    with open(_CONFIG_DIR / "config.yaml", "w") as config_file:
        config = {
            "save_directory": save_path,
            "log_directory": log_path,
            "enable_logging": enable_logging,
        }

        dump(config, config_file)


def load_config():
    """Set logging and saving parameters based on yaml conf file.

    Raises:
        errors.NoSavePath: If config file save path is empty
        errors.InvalidSavePath: If config file save path is invalid
        errors.InvalidLogPath: If config file log path is invalid
    """

    with open(_CONFIG_DIR / "config.yaml", "r") as config_file:
        config = load(config_file, Loader=FullLoader)

    if config["save_directory"] == "":
        raise errors.NoSavePath
    if not path_is_valid(config["save_directory"]):
        raise errors.InvalidSavePath

    SAVER.save_path = config["save_directory"]

    if config["enable_logging"]:
        LOGGER.log_enabled = True
    else:
        return

    if config["log_directory"] == "":
        LOGGER.disable_logging()
    elif not path_is_valid(config["log_directory"]):
        raise errors.InvalidLogPath
    else:
        LOGGER.log_file_path = config["log_directory"]
