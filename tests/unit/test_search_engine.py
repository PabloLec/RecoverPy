import pytest

from tests.fixtures.mock_grep_process import GREP_RESULT_COUNT
from tests.integration.helper import assert_with_timeout


def test_search_params(search_engine):
    assert search_engine.search_params.partition == "/dev/sda1"
    assert search_engine.search_params.searched_lines == ["Lorem ipsum"]


def test_search_progress_before_search(search_engine):
    assert search_engine.search_progress.result_count == 0
    assert int(search_engine.search_progress.progress_percent) == 0


@pytest.mark.asyncio
async def test_start_search(search_engine):
    await search_engine.start_search()

    assert search_engine._grep_process.returncode is None


@pytest.mark.asyncio
async def test_search_progress_after_search(search_engine):
    await assert_with_timeout(
        lambda: search_engine.search_progress.result_count == GREP_RESULT_COUNT,
        GREP_RESULT_COUNT,
        search_engine.search_progress.result_count,
    )
    assert int(search_engine.search_progress.progress_percent) == 100


def test_list_items_queue_size(search_engine):
    assert search_engine.formatted_results_queue.qsize() == GREP_RESULT_COUNT


def test_list_items_queue_content(search_engine):
    expected_list_items = [
        [1, "Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed do "],
        [2, "Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed da "],
        [3, "Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed du"],
    ]

    results = []
    while not search_engine.formatted_results_queue.empty():
        results.append(search_engine.formatted_results_queue.get_nowait())

    for i, result in enumerate(results):
        assert expected_list_items[i][0] == result.inode
        assert expected_list_items[i][1] == result.line
