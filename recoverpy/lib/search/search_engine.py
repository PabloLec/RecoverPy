from __future__ import annotations

from asyncio import Queue as AsyncQueue
from asyncio import new_event_loop
from queue import Queue
from subprocess import Popen
from time import sleep

from recoverpy.lib.search.result_processor import ResultProcessor
from recoverpy.lib.search.thread_factory import (
    start_grep_process,
    start_progress_monitoring_thread,
    start_result_dequeue_thread,
    start_result_enqueue_thread,
)
from recoverpy.models.grep_result import GrepResult
from recoverpy.models.search_params import SearchParams
from recoverpy.models.search_progress import SearchProgress


class SearchEngine:
    """Core search class spawning a grep process and multiple threads to monitor
    and consume its output.
    """

    _grep_process: Popen[bytes]

    def __init__(self, partition: str, searched_string: str):
        self.search_params = SearchParams(partition, searched_string)
        self.search_progress = SearchProgress()
        self.result_processor = ResultProcessor(self.search_params)
        self.results_queue: Queue[bytes] = Queue()
        self.list_items_queue: AsyncQueue[GrepResult] = AsyncQueue()

    async def start_search(self) -> None:
        self._grep_process = start_grep_process(
            searched_string=self.search_params.searched_lines[0],
            partition=self.search_params.partition,
        )
        start_result_enqueue_thread(self._grep_process, self.results_queue)
        start_result_dequeue_thread(self.dequeue_results)
        start_progress_monitoring_thread(self._grep_process, self.search_progress)

    def dequeue_results(self) -> None:
        loop = new_event_loop()
        while True:
            results = self.result_processor.get_new_results(self.results_queue)
            for result in results:
                grep_result = self.create_grep_result(
                    result, self.search_progress.result_count
                )
                loop.run_until_complete(self.list_items_queue.put(grep_result))
                self.search_progress.result_count += 1
            sleep(0.1)

    def create_grep_result(self, result: str, result_index: int) -> GrepResult:
        grep_result = GrepResult(result)
        grep_result.inode = self.result_processor.fix_inode(grep_result.inode)
        grep_result.line = self.result_processor.fix_line_start(grep_result.line)
        grep_result.create_list_item(
            "grep-result-odd" if result_index % 2 == 0 else "grep-result-even"
        )
        return grep_result

    def stop_search(self) -> None:
        self._grep_process.kill()
