from time import sleep

import pytest

from tests.fixtures.mock_grep_process import GREP_RESULT_COUNT


def test_search_params(search_engine):
    assert search_engine.search_params.partition == "/dev/sda1"
    assert search_engine.search_params.searched_lines == ["Lorem ipsum"]


def test_search_progress_before_search(search_engine):
    assert search_engine.search_progress.result_count == 0
    assert search_engine.search_progress.progress_percent == 0.0


@pytest.mark.asyncio
async def test_start_search(search_engine):
    await search_engine.start_search()

    assert search_engine._grep_process.returncode is None


def test_search_progress_after_search(search_engine):
    sleep(0.5)
    assert search_engine.search_progress.result_count == GREP_RESULT_COUNT
    assert search_engine.search_progress.progress_percent == 100.0


def test_list_items_queue_size(search_engine):
    assert search_engine.list_items_queue.qsize() == GREP_RESULT_COUNT


def test_list_items_queue_content(search_engine):
    expected_list_items = [
        [1, "Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed do "],
        [2, "Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed da "],
        [3, "Lorem ipsum dolor sit amet, test consectetur adipiscing elit, sed du"],
    ]

    results = []
    while not search_engine.list_items_queue.empty():
        results.append(search_engine.list_items_queue.get_nowait())

    for i, result in enumerate(results):
        assert expected_list_items[i][0] == result.inode
        assert expected_list_items[i][1] == result.line
