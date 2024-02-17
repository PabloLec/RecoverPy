"""
SearchEngine initiates the search process upon request from the UI.
A Grep process is started with the requested parameters along with subthreads acting as workers.
The first thread consumes the standard output from Grep and simply enqueues each line into a first queue.
A second thread consumes this queue, filters and formats the raw strings into objects ready to be integrated
into the UI and finally stores these objects in an asynchronous queue to be consumed by the UI.
"""

from __future__ import annotations

from asyncio import AbstractEventLoop
from asyncio import Queue as AsyncQueue
from asyncio import new_event_loop
from io import BufferedReader
from queue import Queue
from subprocess import Popen
from typing import List

from magika import Magika

from recoverpy.lib.helper import get_dd_output, decode_result, get_inode
from recoverpy.lib.search.thread_factory import (
    start_grep_process,
    start_progress_monitoring_thread,
    start_result_converter_thread,
    start_grep_stdout_consumer_thread,
)
from recoverpy.log.logger import log
from recoverpy.models.grep_result import GrepResult
from recoverpy.models.raw_result import RawResult
from recoverpy.models.search_params import SearchParams
from recoverpy.models.search_progress import SearchProgress

magika = Magika()


def _consume_grep_stdout(out: BufferedReader, queue: Queue[bytes]) -> None:
    log.debug("grep_consumer - Grep output enqueue thread started")
    for line in iter(out.readline, b""):
        queue.put(line)
    out.close()


class SearchEngine:
    _grep_process: Popen[bytes]
    _seen_inodes: set[int] = set()

    def __init__(self, partition: str, searched_string: str):
        self.search_params = SearchParams(partition, searched_string)
        self.search_progress = SearchProgress()
        self.raw_grep_results_queue: Queue[bytes] = Queue()
        self.formatted_results_queue: AsyncQueue[GrepResult] = AsyncQueue()

    async def start_search(self) -> None:
        self._start_grep_process()
        self._start_auxiliary_threads()

    def stop_search(self) -> None:
        self._grep_process.kill()

    def _start_grep_process(self) -> None:
        self._grep_process = start_grep_process(
            searched_string=self.search_params.searched_lines[0],
            partition=self.search_params.partition,
        )

    def _start_auxiliary_threads(self) -> None:
        start_grep_stdout_consumer_thread(
            _consume_grep_stdout, self._grep_process, self.raw_grep_results_queue
        )
        start_result_converter_thread(self._convert_results)
        start_progress_monitoring_thread(self._grep_process, self.search_progress)

    def _convert_results(self) -> None:
        """Initiate formatting and filtering of raw grep results.
        A new event loop is created to interact with the async queue."""
        loop = new_event_loop()
        while True:
            results = self._decode_new_results(self.raw_grep_results_queue)
            self._process_new_results(results, loop)
            log.debug(f"search_engine - Dequeued {len(results)} results")

    def _decode_new_results(self, queue_object: Queue[bytes]) -> List[RawResult]:
        """Consume raw grep results, filter out false positives if multiline and return decoded results."""
        queue_list: List[bytes] = list(queue_object.queue)
        queue_size = len(queue_list)
        queue_object.queue.clear()
        if queue_size == 0:
            return []

        return [
            RawResult(decode_result(r), magika.identify_bytes(r)) for r in queue_list
        ]

    def _filter_multiline_results(self, results: List[str]) -> List[str]:
        """Filter out false positives from multiline results."""
        return [result for result in results if self._is_result_valid(result)]

    def _is_result_valid(self, result: str) -> bool:
        """Check if result contains all searched lines."""
        inode = int(get_inode(result))
        block_factor = self.search_params.block_size * 8

        both_block_output = self._get_combined_block_output(inode, block_factor)
        return all(
            line in both_block_output for line in self.search_params.searched_lines
        )

    def _get_combined_block_output(self, inode: int, block_factor: int) -> str:
        """Get combined output of current and next block."""
        block_index = inode // block_factor
        block_output = get_dd_output(
            self.search_params.partition, block_factor, block_index
        )
        next_block_output = get_dd_output(
            self.search_params.partition, block_factor, block_index + 1
        )

        return decode_result(block_output) + decode_result(next_block_output)

    def _process_new_results(
        self, results: List[RawResult], loop: AbstractEventLoop
    ) -> None:
        """Consumes grep result strings, convert them into GrepResult objects
        and enqueues them into the formatted results queue for UI."""
        for result in results:
            grep_result = self._create_grep_result(
                result, self.search_progress.result_count
            )

            if grep_result.inode in self._seen_inodes:
                continue

            self._seen_inodes.add(grep_result.inode)
            loop.run_until_complete(self.formatted_results_queue.put(grep_result))
            self.search_progress.result_count += 1

    def _create_grep_result(self, result: RawResult, result_index: int) -> GrepResult:
        """Create a GrepResult object from a raw grep result string."""
        grep_result = GrepResult(result)
        self._configure_grep_result(grep_result, result_index)
        log.debug(f"search_engine - Created grep result {grep_result.inode}")
        return grep_result

    def _configure_grep_result(
        self, grep_result: GrepResult, result_index: int
    ) -> None:
        """Fix inode number and line start then sets the CSS class for the UI."""
        grep_result.inode = self._fix_inode(grep_result.inode)
        grep_result.line = self._fix_line_start(grep_result.line)
        grep_result.css_class = (
            "grep-result-odd" if result_index % 2 == 0 else "grep-result-even"
        )

    def _fix_inode(self, inode: int) -> int:
        """Shift inode to the first block containing the searched string."""
        inode //= self.search_params.block_size

        for _ in range(10):
            dd_output = get_dd_output(
                self.search_params.partition, self.search_params.block_size, inode
            )
            if self.search_params.searched_lines[0] in decode_result(dd_output):
                return inode
            inode += 1
        return inode

    def _fix_line_start(self, line: str) -> str:
        """Remove unnecessary characters from the start of the line to improve readability."""
        result_index: int = line.find(self.search_params.searched_lines[0])
        return line[min(result_index, 15) :]
