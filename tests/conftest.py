from pathlib import Path

import pytest

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
    session_mocker.patch("recoverpy.utils.helper.is_user_root", return_value=True)


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
    return SCREENS_HANDLER.screens["search"]


@pytest.fixture(scope="module")
def BLOCK_SCREEN(SCREENS_HANDLER):
    SCREENS_HANDLER.open_screen("block", partition="/dev/test", initial_block=0)
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
    mocker.patch("recoverpy.utils.helper.geteuid", return_value=0)


@pytest.fixture(scope="function")
def USER_IS_NOT_ROOT(mocker):
    mocker.patch("recoverpy.utils.helper.geteuid", return_value=1)
