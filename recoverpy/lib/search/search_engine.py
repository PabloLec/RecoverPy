import asyncio
from asyncio import ensure_future
from queue import Queue
from subprocess import Popen
from time import sleep

from lib.search.thread_factory import (
    start_grep_process,
    start_result_dequeue_thread,
    start_result_enqueue_thread,
)
from models.grep_result import GrepResult

from lib.search.result_processor import ResultProcessor
from models.search_params import SearchParams

from models.search_progress import SearchProgress

from lib.search.thread_factory import start_progress_monitoring_thread


class SearchEngine:
    """Core search class spawning a grep process and multiple threads to monitor
    and consume its output.
    """

    def __init__(self, partition: str, searched_string: str):
        self.search_params = SearchParams(partition, searched_string)
        self.search_progress = SearchProgress()
        self.result_processor = ResultProcessor(self.search_params)
        self.results_queue = Queue()
        self.list_items_queue = asyncio.Queue()

    async def start_search(self):
        grep_process: Popen = start_grep_process(
            searched_string=self.search_params.searched_lines[0],
            partition=self.search_params.partition,
        )
        start_result_enqueue_thread(grep_process, self.results_queue)
        start_result_dequeue_thread(self.dequeue_results)
        start_progress_monitoring_thread(grep_process, self.search_progress)


    def dequeue_results(self):
        loop = asyncio.new_event_loop()
        while True:
            results = self.result_processor.get_new_results(self.results_queue)
            for result in results:
                grep_result = self.create_grep_result(result, self.search_progress.result_count)
                loop.run_until_complete(self.list_items_queue.put(grep_result))
                self.search_progress.result_count += 1
            sleep(0.1)

    def create_grep_result(self, result: str, result_index: int) -> GrepResult:
        grep_result = GrepResult(result)
        grep_result.inode = self.result_processor.fix_block_number(grep_result.inode)
        grep_result.line = self.result_processor.fix_line_start(grep_result.line)
        grep_result.create_list_item("grep-result-odd" if result_index % 2 == 0 else "grep-result-even")
        return grep_result

