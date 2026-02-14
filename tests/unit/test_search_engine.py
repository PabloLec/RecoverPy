from threading import Thread
from time import sleep

import pytest

import recoverpy.lib.search.search_engine as search_engine_module
from recoverpy.lib.search.scanner import ScanHit
from tests.fixtures.mock_scan_hits import SCAN_HIT_COUNT
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
    assert search_engine._scan_thread is not None
    assert search_engine._convert_thread is not None


@pytest.mark.asyncio
async def test_search_progress_after_search(search_engine):
    await assert_with_timeout(
        lambda: search_engine.search_progress.result_count == SCAN_HIT_COUNT,
        SCAN_HIT_COUNT,
        search_engine.search_progress.result_count,
    )
    assert int(search_engine.search_progress.progress_percent) == 100


def test_list_items_queue_size(search_engine):
    assert search_engine.formatted_results_queue.qsize() == SCAN_HIT_COUNT


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


@pytest.mark.asyncio
async def test_stop_search_sets_cancel_flag(search_engine):
    await search_engine.start_search()
    search_engine.stop_search()
    assert search_engine._stop_event.is_set() is True


def test_raw_hits_queue_is_bounded_with_backpressure(mocker):
    engine = search_engine_module.SearchEngine(
        partition="/dev/sda1", searched_string="Lorem ipsum"
    )

    def many_hits(*args, **kwargs):
        for i in range(search_engine_module._RAW_HITS_QUEUE_MAXSIZE + 500):
            yield ScanHit(match_offset=i * 4096, preview=b"preview")

    mocker.patch.object(search_engine_module, "iter_scan_hits", side_effect=many_hits)

    thread = Thread(target=engine._scan_hits_worker, daemon=True)
    thread.start()
    sleep(0.3)

    assert engine.raw_scan_hits_queue.qsize() <= engine.raw_scan_hits_queue.maxsize
    assert engine.raw_scan_hits_queue.maxsize == search_engine_module._RAW_HITS_QUEUE_MAXSIZE

    engine._stop_event.set()
    thread.join(timeout=2.0)
    assert thread.is_alive() is False
