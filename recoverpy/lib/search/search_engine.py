import asyncio
from queue import Queue
from subprocess import Popen
from asyncio import ensure_future, to_thread
from time import sleep
from typing import Optional, Callable
from psutil import Process

from models.progress import Progress

from lib.helper import decode_result, get_inode, get_block_size
from lib.meta_singleton import SingletonMeta
from lib.search.static import (
    format_multine_line_results,
    get_dd_output,
    start_grep_process,
    start_progress_monitoring_thread,
    start_result_dequeue_thread,
    start_result_enqueue_thread,
)

from lib.search.static import enqueue_grep_output
from textual._types import MessageTarget
from textual.message import Message


class Results:
    def __init__(self, lines=None, block_index: int = 0):
        if lines is None:
            lines = list()
        self.lines: list = lines
        self.block_index: int = block_index

    def is_empty(self):
        return len(self.lines) == 0


class SearchEngine(metaclass=SingletonMeta):
    """Core search class spawning a grep process and multiple threads to monitor
    and consume its output.
    """

    class NewResults(Message):
        def __init__(self, sender: MessageTarget, results: Results) -> None:
            self.results = results
            super().__init__(sender)

    def __init__(self, partition: str, searched_string: str):
        self.partition: str = partition
        self.block_size: int = get_block_size(partition)
        self.searched_lines: list = searched_string.strip().splitlines()
        self.is_multi_line: Optional[bool] = len(self.searched_lines) > 1
        self.new_results_callback = None
        self.queue = Queue()
        self.block_index: int = 0

    async def start_search(self, search_sreen, progress_callback: Callable):
        grep_process: Popen = start_grep_process(
            searched_string=self.searched_lines[0],
            partition=self.partition,
        )
        start_result_enqueue_thread(grep_process, self.queue)
        start_result_dequeue_thread(self.dequeue_results, search_sreen)

    def dequeue_results(self, search_sreen):
        loop = asyncio.new_event_loop()
        while True:
            results: Results = self.get_new_results(
                self.queue, self.block_index
            )
            self.block_index = results.block_index
            if not results.is_empty():
                loop.run_until_complete(search_sreen.post_message(self.NewResults(search_sreen, results)))
            sleep(0.1)
    def post_result(self, result: str):
        self.new_results_callback(result)

    def get_new_results(self, queue_object: Queue, current_blockindex: int) -> Results:
        """Consume grep output queue and format results."""

        queue_list: list = list(queue_object.queue)
        queue_size = len(queue_list)
        queue_object.queue.clear()
        if queue_size == 0:
            return Results(block_index=current_blockindex)

        new_block_index: int = current_blockindex + queue_size
        one_lined_results: list = format_multine_line_results(queue_list)

        if not self.is_multi_line:
            return Results(lines=one_lined_results, block_index=new_block_index)

        final_results = [
            result
            for result in one_lined_results
            if self.is_result_format_valid(result)
        ]
        return Results(lines=final_results, block_index=new_block_index)

    def is_result_format_valid(self, result) -> bool:
        """Check if all searched lines are present in result block and next adjacent
        block, else result is a false positive and will not be displayed.
        """

        inode: int = int(get_inode(result))
        block_output: bytes = get_dd_output(
            self.partition, self.block_size * 8, int(inode / (self.block_size * 8))
        )
        next_block_output: bytes = get_dd_output(
            self.partition, self.block_size * 8, int(inode / (self.block_size * 8) + 1)
        )
        both_block_output: str = decode_result(block_output) + decode_result(
            next_block_output
        )
        return all(line in both_block_output for line in self.searched_lines)

    def fix_block_number(self, block_number: str) -> str:
        """Fix result block number if search string is too far from beginning of
        returned inode number.
        """

        fixed_block = int(block_number)
        for _ in range(10):
            dd_output: str = decode_result(
                get_dd_output(self.partition, self.block_size, fixed_block)
            )
            if self.searched_lines[0] in dd_output:
                return str(fixed_block)
            fixed_block += 1
        return block_number
