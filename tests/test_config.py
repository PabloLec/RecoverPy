from os import environ

import pytest

from recoverpy.config.config import write_config_to_file
from recoverpy.config.setup import setup
from recoverpy.lib.errors import InvalidLogPath, InvalidSavePath, NoSavePath
from recoverpy.lib.helper import is_user_root
from recoverpy.lib.logger import LOGGER
from recoverpy.lib.saver import Saver


def test_no_save_path(mock_config):
    with pytest.raises(NoSavePath):
        write_config_to_file(save_path="", log_path=mock_config, enable_logging=False)


def test_invalid_save_path(mock_config):
    with pytest.raises(InvalidSavePath):
        write_config_to_file(
            save_path="/foo/bar", log_path=mock_config, enable_logging=False
        )


def test_no_log_path(mock_config):
    write_config_to_file(save_path=mock_config, log_path="", enable_logging=True)

    assert not LOGGER.log_enabled


def test_invalid_log_path(mock_config):
    with pytest.raises(InvalidLogPath):
        write_config_to_file(
            save_path=mock_config, log_path="/foo/bar", enable_logging=True
        )


def test_conf_parsing(mock_config):
    write_config_to_file(
        save_path=mock_config, log_path=mock_config, enable_logging=True
    )

    assert Saver().save_path == mock_config
    assert LOGGER.log_path == mock_config


def test_missing_dependencies(MISSING_DEPENDENCY):
    with pytest.raises(OSError):
        setup()


def test_terminal_env_var_fix():
    environ["TERM"] = "test"
    setup()

    assert environ["TERM"] == "xterm-256color"


def test_user_root(PARAMETERS_SCREEN, USER_IS_ROOT):
    assert is_user_root(PARAMETERS_SCREEN.master) is True


def test_user_not_root(PARAMETERS_SCREEN, USER_IS_NOT_ROOT):
    assert is_user_root(PARAMETERS_SCREEN.master) is False
