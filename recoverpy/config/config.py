from pathlib import Path

from yaml import FullLoader, load

from recoverpy.utils import errors
from recoverpy.utils.logger import LOGGER
from recoverpy.utils.saver import SAVER


def parse_configuration():
    """Set logging and saving parameters based on yaml conf file.

    Raises:
        errors.NoSavePath: If config file save path is empty
        errors.InvalidSavePath: If config file save path is invalid
        errors.InvalidLogPath: If config file log path is invalid
    """
    project_path = Path(__file__).parent.absolute()

    with open(project_path / "config.yaml") as config_file:
        config = load(config_file, Loader=FullLoader)

    if config["save_directory"] == "":
        raise errors.NoSavePath
    if not Path(config["save_directory"]).is_dir():
        raise errors.InvalidSavePath

    SAVER.save_path = config["save_directory"]

    if config["enable_logging"]:
        LOGGER.enable_logging()
    else:
        return

    if config["log_directory"] == "":
        LOGGER.disable_logging()
    elif not Path(config["log_directory"]).is_dir():
        raise errors.InvalidLogPath
    else:
        LOGGER.set_log_file_path(config["log_directory"])
