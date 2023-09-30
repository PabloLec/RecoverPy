from __future__ import annotations

from asyncio import AbstractEventLoop
from asyncio import Queue as AsyncQueue
from asyncio import new_event_loop
from queue import Queue
from subprocess import Popen
from time import sleep
from typing import List

from recoverpy.lib.search.result_processor import ResultProcessor
from recoverpy.lib.search.thread_factory import (
    start_grep_process,
    start_progress_monitoring_thread,
    start_result_dequeue_thread,
    start_result_enqueue_thread,
)
from recoverpy.log.logger import log
from recoverpy.models.grep_result import GrepResult
from recoverpy.models.search_params import SearchParams
from recoverpy.models.search_progress import SearchProgress


class SearchEngine:
    _grep_process: Popen[bytes]
    _seen_inodes: set[int] = set()

    def __init__(self, partition: str, searched_string: str):
        self._initialize_search_components(partition, searched_string)
        self.results_queue: Queue[bytes] = Queue()
        self.list_items_queue: AsyncQueue[GrepResult] = AsyncQueue()

    def _initialize_search_components(
        self, partition: str, searched_string: str
    ) -> None:
        self.search_params = SearchParams(partition, searched_string)
        self.search_progress = SearchProgress()
        self.result_processor = ResultProcessor(self.search_params)

    async def start_search(self) -> None:
        self._initialize_grep_process()
        self._start_auxiliary_threads()

    def stop_search(self) -> None:
        self._grep_process.kill()

    def _initialize_grep_process(self) -> None:
        self._grep_process = start_grep_process(
            searched_string=self.search_params.searched_lines[0],
            partition=self.search_params.partition,
        )

    def _start_auxiliary_threads(self) -> None:
        start_result_enqueue_thread(self._grep_process, self.results_queue)
        start_result_dequeue_thread(self._dequeue_results)
        start_progress_monitoring_thread(self._grep_process, self.search_progress)

    def _dequeue_results(self) -> None:
        loop = new_event_loop()
        while True:
            results = self.result_processor.get_new_results(self.results_queue)
            self._add_new_results(results, loop)
            log.debug(f"search_engine - Dequeued {len(results)} results")
            sleep(0.1)

    def _add_new_results(self, results: List[str], loop: AbstractEventLoop) -> None:
        for result in results:
            grep_result = self._create_grep_result(
                result, self.search_progress.result_count
            )

            if grep_result.inode not in self._seen_inodes:
                self._seen_inodes.add(grep_result.inode)
                loop.run_until_complete(self.list_items_queue.put(grep_result))
                self.search_progress.result_count += 1

    def _create_grep_result(self, result: str, result_index: int) -> GrepResult:
        grep_result = GrepResult(result)
        self._configure_grep_result(grep_result, result_index)
        log.debug(f"search_engine - Created grep result {grep_result.inode}")
        return grep_result

    def _configure_grep_result(
        self, grep_result: GrepResult, result_index: int
    ) -> None:
        grep_result.inode = self.result_processor.fix_inode(grep_result.inode)
        grep_result.line = self.result_processor.fix_line_start(grep_result.line)
        grep_result.css_class = (
            "grep-result-odd" if result_index % 2 == 0 else "grep-result-even"
        )
