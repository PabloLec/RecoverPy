from unittest.mock import MagicMock

import pytest
from .fixtures import lsblk_output, dd_output, grep_output

@pytest.fixture(scope="session", autouse=True)
def system_calls_mock(session_mocker):
    session_mocker.patch(
        "recoverpy.lib.search.thread_factory.start_grep_process", new=grep_output.start_grep_process
    )
    session_mocker.patch("recoverpy.lib.helper.get_dd_output", return_value=dd_output.MOCK_DD_OUTPUT)
    session_mocker.patch(
        "recoverpy.lib.lsblk._lsblk", return_value=lsblk_output.MOCK_LSBLK_OUTPUT
    )
    session_mocker.patch(
        "recoverpy.lib.helper.get_block_size", MagicMock(return_value=4096)
    )