from pathlib import Path
from time import sleep
from unittest.mock import MagicMock

import pytest

import recoverpy

from .fixtures.mock_dd_output import DD_OUTPUT
from .fixtures.mock_grep import start_grep_process
from .fixtures.mock_lsblk_output import MOCK_LSBLK_OUTPUT


@pytest.fixture(scope="session", autouse=True)
def global_mock(session_mocker):
    session_mocker.patch.object(
        recoverpy.lib.search.SearchEngine,
        "start_grep_process",
        new=start_grep_process,
    )
    session_mocker.patch(
        "recoverpy.lib.search.SearchEngine.get_dd_output",
        MagicMock(return_value=DD_OUTPUT),
    )
    session_mocker.patch("py_cui.curses.wrapper", return_value=None)
    session_mocker.patch("recoverpy.lib.helper.lsblk", return_value=MOCK_LSBLK_OUTPUT)
    session_mocker.patch("recoverpy.lib.helper.is_user_root", return_value=True)
    session_mocker.patch(
        "recoverpy.lib.helper.get_block_size", MagicMock(return_value=4096)
    )
    session_mocker.patch(
        "recoverpy.ui.screen_with_block_display.get_block_size",
        MagicMock(return_value=4096),
    )
    session_mocker.patch(
        "recoverpy.ui.screen_search.get_block_size", MagicMock(return_value=4096)
    )


@pytest.fixture(scope="session", autouse=True)
def mock_config(session_mocker, tmpdir_factory):
    test_dir = tmpdir_factory.mktemp("test_dir")
    session_mocker.patch("recoverpy.config.config._CONFIG_DIR", test_dir)
    recoverpy.config.config.write_config_to_file(
        save_path=str(test_dir), log_path=str(test_dir), enable_logging=True
    )
    return Path(test_dir)


@pytest.fixture(scope="session")
def SCREENS_HANDLER():
    return recoverpy.ui.handler.SCREENS_HANDLER


@pytest.fixture(scope="module")
def PARAMETERS_SCREEN(SCREENS_HANDLER):
    SCREENS_HANDLER.open_screen("parameters")
    return SCREENS_HANDLER.screens["parameters"]


@pytest.fixture(scope="module")
def SEARCH_SCREEN(SCREENS_HANDLER):
    SCREENS_HANDLER.open_screen(
        "search", partition="/dev/test", string_to_search="test"
    )
    sleep(2.5)
    return SCREENS_HANDLER.screens["search"]


@pytest.fixture(scope="module")
def BLOCK_SCREEN(SCREENS_HANDLER):
    SCREENS_HANDLER.open_screen("block", partition="/dev/test", initial_block=0)
    sleep(2.5)
    return SCREENS_HANDLER.screens["block"]


@pytest.fixture(scope="module")
def CONFIG_SCREEN(SCREENS_HANDLER):
    SCREENS_HANDLER.open_screen("config")
    return SCREENS_HANDLER.screens["config"]


@pytest.fixture(scope="function")
def MISSING_DEPENDENCY(mocker):
    mocker.patch("recoverpy.config.setup.is_dependency_installed", return_value=False)


@pytest.fixture(scope="function")
def USER_IS_ROOT(mocker):
    mocker.patch("recoverpy.lib.helper.geteuid", return_value=0)


@pytest.fixture(scope="function")
def USER_IS_NOT_ROOT(mocker):
    mocker.patch("recoverpy.lib.helper.geteuid", return_value=1)
