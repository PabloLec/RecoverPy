from contextlib import asynccontextmanager
from unittest.mock import MagicMock

import pytest

from recoverpy.lib.search.search_engine import SearchEngine
from recoverpy.ui.app import RecoverpyApp

from .fixtures import (
    mock_dd_output,
    mock_grep_process,
    mock_lsblk_output,
    mock_progress,
)

TEST_BLOCK_SIZE = 4096


@pytest.fixture(scope="module", autouse=True)
def system_calls_mock(session_mocker):
    session_mocker.patch(
        "recoverpy.lib.search.search_engine.start_grep_process",
        new=mock_grep_process.mock_start_grep_process,
    )
    session_mocker.patch(
        "recoverpy.lib.search.result_processor.get_dd_output",
        side_effect=mock_dd_output.mock_dd_string_output,
    )
    session_mocker.patch(
        "recoverpy.ui.screens.screen_result.get_dd_output",
        side_effect=mock_dd_output.mock_dd_string_output,
    )
    session_mocker.patch(
        "recoverpy.lib.lsblk._lsblk", return_value=mock_lsblk_output.MOCK_LSBLK_OUTPUT
    )
    session_mocker.patch(
        "recoverpy.models.search_params.get_block_size",
        MagicMock(return_value=TEST_BLOCK_SIZE),
    )
    session_mocker.patch(
        "recoverpy.lib.search.thread_factory.is_dependency_installed",
        MagicMock(return_value=True),
    )
    session_mocker.patch(
        "recoverpy.lib.search.thread_factory.monitor_search_progress",
        new=mock_progress.mock_monitor_search_progress,
    )


@pytest.fixture(scope="function")
@asynccontextmanager
async def pilot():
    app = RecoverpyApp()
    async with app.run_test() as pilot_instance:
        yield pilot_instance


@pytest.fixture(scope="module")
def search_engine():
    return SearchEngine(partition="/dev/sda1", searched_string="Lorem ipsum")
