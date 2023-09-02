import asyncio
import inspect

from textual.pilot import Pilot
from textual.widgets import RichLog

from tests.conftest import TEST_BLOCK_SIZE
from tests.fixtures.mock_dd_output import mock_dd_string_output

TEST_PARTITION = "sdb1"
TEST_FULL_PARTITION = "/dev/sdb1"


def get_block_content_text(block_content: RichLog):
    return (
        "".join([line.text for line in block_content.lines])
        .replace(" ", "")
        .replace("\n", "")
    )


def get_expected_block_content_text(inode: int):
    return (
        mock_dd_string_output(TEST_FULL_PARTITION, TEST_BLOCK_SIZE, inode)
        .decode()
        .replace(" ", "")
        .replace("\n", "")
    )


async def assert_with_timeout(check_func, timeout=5.0, interval=0.1):
    end_time = asyncio.get_event_loop().time() + timeout
    while True:
        if check_func():
            return
        if asyncio.get_event_loop().time() > end_time:
            func_src = inspect.getsource(check_func).strip()
            assert (
                False
            ), f"Timeout reached before condition in `{func_src}` became true."
        await asyncio.sleep(interval)


async def assert_current_result_is_selected_for_save(p: Pilot):
    await assert_with_timeout(
        lambda: p.app.screen._inode in p.app.screen._saver._results
    )
    assert p.app.screen._saver._results[p.app.screen._inode].replace(" ", "").replace(
        "\n", ""
    ) == get_expected_block_content_text(p.app.screen._inode)
