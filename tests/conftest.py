import pytest
from .fixtures import lsblk_output

@pytest.fixture(scope="session", autouse=True)
def global_mock(session_mocker):
    session_mocker.patch(
        "recoverpy.lib.lsblk._lsblk", return_value=lsblk_output.MOCK_LSBLK_OUTPUT
    )