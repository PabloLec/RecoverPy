from os import environ
from pathlib import Path

import pytest
import yaml

import recoverpy

_CONFIG_FILE_PATH = Path(recoverpy.__file__).parent.absolute() / "config.yaml"


def set_config(save_directory: str = "/tmp/", log_directory: str = "/tmp/"):
    config = {
        "save_directory": save_directory,
        "enable_logging": True,
        "log_directory": log_directory,
    }

    with open(_CONFIG_FILE_PATH, "w") as file:
        yaml.dump(config, file)


def test_no_save_path():
    set_config(save_directory="")

    with pytest.raises(recoverpy.utils.errors.NoSavePath):
        recoverpy.parse_configuration()


def test_invalid_save_path():
    set_config(save_directory="/foo/bar")

    with pytest.raises(recoverpy.utils.errors.InvalidSavePath):
        recoverpy.parse_configuration()


def test_no_log_path():
    set_config(log_directory="")
    recoverpy.parse_configuration()

    assert not recoverpy._LOGGER._log_enabled


def test_invalid_log_path():
    set_config(log_directory="/foo/bar")

    with pytest.raises(recoverpy.utils.errors.InvalidLogPath):
        recoverpy.parse_configuration()


def test_conf_parsing():
    set_config()
    recoverpy.parse_configuration()

    assert recoverpy._SAVER._save_path == "/tmp/"
    assert recoverpy._LOGGER._log_path == "/tmp/"


def test_terminal_fix():
    environ["TERM"] = "Dummy value"
    recoverpy.verify_terminal_conf()

    assert environ["TERM"] == "xterm-256color"
