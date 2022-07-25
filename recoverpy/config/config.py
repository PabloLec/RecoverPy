from os import X_OK, access
from pathlib import Path

from yaml import FullLoader, dump, load

from recoverpy.lib import errors
from recoverpy.lib.logger import Logger
from recoverpy.lib.saver import Saver

_CONFIG_DIR = Path(__file__).parent.absolute()


def is_path_valid(string_path: str) -> bool:
    path: Path = Path(string_path)
    try:
        if not path.is_dir():
            return False
    except PermissionError:
        return False

    return access(path, X_OK)


def write_config_to_file(save_path: str, log_path: str, enable_logging: bool):
    with open(_CONFIG_DIR / "config.yaml", "w") as config_file:
        config: dict = {
            "save_directory": str(save_path),
            "log_directory": str(log_path),
            "enable_logging": enable_logging,
        }

        dump(config, config_file)
    load_config()


def load_config():
    with open(_CONFIG_DIR / "config.yaml", "r") as config_file:
        config: dict = load(config_file, Loader=FullLoader)

    if "save_directory" not in config or config["save_directory"] == "":
        raise errors.NoSavePath
    if not is_path_valid(config["save_directory"]):
        raise errors.InvalidSavePath

    Saver().save_path = Path(config["save_directory"])

    if "log_directory" not in config or config["log_directory"] == "":
        Logger().log_enabled = False
    elif not is_path_valid(config["log_directory"]):
        raise errors.InvalidLogPath
    else:
        Logger().log_path = Path(config["log_directory"])
        Logger().log_enabled = bool(config["enable_logging"])

    if Logger().log_enabled:
        Logger().start_logging()
