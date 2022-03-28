import pytest

from recoverpy.config.config import write_config_to_file
from recoverpy.utils.errors import InvalidLogPath, InvalidSavePath, NoSavePath
from recoverpy.utils.logger import LOGGER
from recoverpy.utils.saver import SAVER


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

    assert SAVER.save_path == mock_config
    assert LOGGER.log_path == mock_config
