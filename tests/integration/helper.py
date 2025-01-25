import asyncio
import inspect

from textual.pilot import Pilot
from textual.widgets import RichLog

from tests.conftest import TEST_BLOCK_SIZE
from tests.fixtures.mock_dd_output import mock_dd_string_output

TEST_PARTITION = "sdb1"
TEST_FULL_PARTITION = "/dev/sdb1"
EXPECTED_SAVE_RESULT = {}


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


async def assert_with_timeout(check_func, expected, actual, timeout=10.0, interval=0.1):
    end_time = asyncio.get_event_loop().time() + timeout
    while True:
        if check_func():
            return
        if asyncio.get_event_loop().time() > end_time:
            func_src = inspect.getsource(check_func).strip()
            assert False, (
                f"Timeout reached before condition in `{func_src}` became true. Expected: {expected}, Actual: {actual}"
            )
        await asyncio.sleep(interval)


async def assert_current_result_is_selected_for_save(p: Pilot):
    await p.pause()

    assert p.app.screen._inode in p.app.screen._saver._results

    assert p.app.screen._saver._results[p.app.screen._inode].replace(" ", "").replace(
        "\n", ""
    ) == get_expected_block_content_text(p.app.screen._inode)


def add_expected_save_result(p: Pilot):
    global EXPECTED_SAVE_RESULT
    EXPECTED_SAVE_RESULT[p.app.screen._inode] = p.app.screen._raw_block_content


def get_expected_save_result():
    global EXPECTED_SAVE_RESULT
    return "\n".join(
        [EXPECTED_SAVE_RESULT[num] for num in sorted(EXPECTED_SAVE_RESULT.keys())]
    )
