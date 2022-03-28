import pytest
from py_cui import PyCUI

import recoverpy

from .fixtures.mock_check_output import check_output
from .fixtures.mock_grep import create_grep_process
from .fixtures.mock_lsblk_output import MOCK_LSBLK_OUTPUT


@pytest.fixture(scope="session", autouse=True)
def global_mock(session_mocker):
    session_mocker.patch.object(
        recoverpy.utils.search.SearchEngine,
        "create_grep_process",
        new=create_grep_process,
    )
    session_mocker.patch.object(
        recoverpy.ui.screen_with_block_display, "check_output", new=check_output
    )
    session_mocker.patch("py_cui.curses.wrapper", return_value=None)
    session_mocker.patch("recoverpy.utils.helper.lsblk", return_value=MOCK_LSBLK_OUTPUT)


@pytest.fixture(scope="session", autouse=True)
def mock_config(session_mocker, tmpdir_factory):
    test_dir = tmpdir_factory.mktemp("test_dir")
    session_mocker.patch("recoverpy.config.config._CONFIG_DIR", test_dir)
    recoverpy.config.config.write_config_to_file(
        save_path=str(test_dir), log_path=str(test_dir), enable_logging=True
    )
    return str(test_dir)


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
    return SCREENS_HANDLER.screens["search"]


@pytest.fixture(scope="module")
def BLOCK_SCREEN(SCREENS_HANDLER):
    SCREENS_HANDLER.open_screen("block", partition="/dev/test", initial_block=0)
    return SCREENS_HANDLER.screens["block"]


@pytest.fixture()
def CONFIG_SCREEN(SCREENS_HANDLER):
    SCREENS_HANDLER.open_screen("config")
    return SCREENS_HANDLER.screens["config"]


@pytest.fixture(scope="session")
def TEST_SEARCH_SCREEN(TEST_FILE):
    return recoverpy.screens.screen_search.SearchScreen(
        master=PyCUI(10, 10),
        partition=TEST_FILE,
        string_to_search="TEST STRING",
    )
