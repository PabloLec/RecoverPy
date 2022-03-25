import pytest
from py_cui import PyCUI

import recoverpy

from .fixtures.lsblk_output import MOCK_LSBLK_OUTPUT
from .fixtures.mock_check_output import check_output
from .fixtures.mock_grep import create_grep_process


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


@pytest.fixture()
def RESULTS_SCREEN():
    screen = recoverpy.screens.screen_results.BlockScreen.__new__(
        recoverpy.screens.screen_results.BlockScreen
    )
    screen.master = PyCUI(10, 10)
    screen.partition = "/dev/sda1"
    screen.saved_blocks_dict = {}
    screen.current_block = 5

    return screen


@pytest.fixture()
def CONFIG_SCREEN():
    screen = recoverpy.screens.screen_config.ConfigScreen.__new__(
        recoverpy.screens.screen_config.ConfigScreen
    )
    screen.master = PyCUI(10, 10)
    screen._log_enabled = True

    return screen


@pytest.fixture(scope="session")
def TEST_FILE(tmp_path_factory):
    lorem = "Integer vitae ultrices magna. Nam non cursus odio. In dapibus augue.\n"
    file = tmp_path_factory.mktemp("data") / "file"
    with file.open("w", encoding="utf-8") as f:
        f.write(lorem * 20000 + "TEST STRING" + lorem * 20000)

    return file


@pytest.fixture(scope="session")
def TEST_SEARCH_SCREEN(TEST_FILE):
    return recoverpy.screens.screen_search.SearchScreen(
        master=PyCUI(10, 10),
        partition=TEST_FILE,
        string_to_search="TEST STRING",
    )
