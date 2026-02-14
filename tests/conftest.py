from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from recoverpy.lib.search.search_engine import SearchEngine

from .fixtures import (
    mock_device_discovery,
    mock_block_reader,
    mock_grep_process,
    mock_progress,
)

TEST_BLOCK_SIZE = 4096


@pytest_asyncio.fixture(scope="session", autouse=True)
def system_calls_mock(session_mocker):
    session_mocker.patch(
        "recoverpy.lib.search.search_engine.start_grep_process",
        new=mock_grep_process.mock_start_grep_process,
    )
    session_mocker.patch(
        "recoverpy.lib.search.search_engine.read_block",
        side_effect=mock_block_reader.mock_read_block_output,
    )
    session_mocker.patch(
        "recoverpy.ui.screens.screen_result.read_block",
        side_effect=mock_block_reader.mock_read_block_output,
    )
    session_mocker.patch(
        "recoverpy.lib.device_discovery._read_proc_mounts",
        return_value=mock_device_discovery.MOCK_PROC_MOUNTS,
    )
    session_mocker.patch(
        "recoverpy.lib.device_discovery._read_proc_partition_sizes",
        return_value=mock_device_discovery.MOCK_PROC_PARTITION_SIZES,
    )
    session_mocker.patch(
        "recoverpy.lib.device_discovery._list_block_devices",
        return_value=mock_device_discovery.MOCK_BLOCK_DEVICES,
    )
    session_mocker.patch(
        "recoverpy.lib.device_discovery._read_device_type",
        side_effect=mock_device_discovery.mock_read_device_type,
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


@pytest.fixture(scope="session")
def search_engine():
    return SearchEngine(partition="/dev/sda1", searched_string="Lorem ipsum")


@pytest.fixture(scope="function")
def mock_root(session_mocker):
    session_mocker.patch(
        "recoverpy.lib.env_check._is_user_root",
        MagicMock(return_value=True),
    )


@pytest.fixture(scope="function")
def mock_not_root(session_mocker):
    session_mocker.patch(
        "recoverpy.lib.env_check._is_user_root",
        MagicMock(return_value=False),
    )


@pytest.fixture(scope="function")
def mock_valid_version(session_mocker):
    session_mocker.patch(
        "recoverpy.lib.env_check._is_version_supported",
        MagicMock(return_value=True),
    )


@pytest.fixture(scope="function")
def mock_invalid_version(session_mocker):
    session_mocker.patch(
        "recoverpy.lib.env_check._is_version_supported",
        MagicMock(return_value=False),
    )


@pytest.fixture(scope="function")
def mock_linux(session_mocker):
    session_mocker.patch(
        "recoverpy.lib.env_check._is_linux",
        MagicMock(return_value=True),
    )


@pytest.fixture(scope="function")
def mock_not_linux(session_mocker):
    session_mocker.patch(
        "recoverpy.lib.env_check._is_linux",
        MagicMock(return_value=False),
    )


@pytest.fixture(scope="function")
def mock_dependencies_installed(session_mocker):
    session_mocker.patch(
        "recoverpy.lib.env_check._are_system_dependencies_installed",
        MagicMock(return_value=True),
    )


@pytest.fixture(scope="function")
def mock_dependencies_not_installed(session_mocker):
    session_mocker.patch(
        "recoverpy.lib.env_check._are_system_dependencies_installed",
        MagicMock(return_value=False),
    )


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords and call.excinfo is not None:
        parent = item.parent
        parent._previousfailed = item


def pytest_runtest_setup(item):
    previousfailed = getattr(item.parent, "_previousfailed", None)
    if previousfailed is not None:
        pytest.skip("previous test failed (%s)" % previousfailed.name)
