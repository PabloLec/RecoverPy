from os import environ
from pathlib import Path

import pytest
import yaml

import recoverpy

_CONFIG_FILE_PATH = (
    Path(recoverpy.__file__).parent.absolute() / "config" / "config.yaml"
)


def set_config(save_directory: str = "/tmp/", log_directory: str = "/tmp/"):
    config = {
        "save_directory": save_directory,
        "enable_logging": False,
        "log_directory": log_directory,
    }

    with open(_CONFIG_FILE_PATH, "w") as file:
        yaml.dump(config, file)


def test_no_save_path():
    set_config(save_directory="")

    with pytest.raises(recoverpy.utils.errors.NoSavePath):
        recoverpy.config.config.load_config()


def test_invalid_save_path():
    set_config(save_directory="/foo/bar")

    with pytest.raises(recoverpy.utils.errors.InvalidSavePath):
        recoverpy.config.config.load_config()


def test_no_log_path():
    set_config(log_directory="")
    recoverpy.config.config.load_config()

    assert not recoverpy.utils.logger.LOGGER.log_enabled


def test_invalid_log_path():
    set_config(log_directory="/foo/bar")

    with pytest.raises(recoverpy.utils.errors.InvalidLogPath):
        recoverpy.config.config.load_config()


def test_conf_parsing():
    set_config()
    recoverpy.config.config.load_config()

    assert recoverpy.utils.saver.SAVER.save_path == "/tmp/"
    assert recoverpy.utils.logger.LOGGER.log_path == "/tmp/"


def test_terminal_fix():
    environ["TERM"] = "Dummy value"
    recoverpy.verify_terminal_conf()

    assert environ["TERM"] == "xterm-256color"
