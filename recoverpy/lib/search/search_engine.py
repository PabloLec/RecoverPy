import asyncio
from dataclasses import dataclass, field
from queue import Queue
from random import randint
from subprocess import Popen
from asyncio import ensure_future, to_thread
from time import sleep
from typing import Optional, Callable, List
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
from textual.widgets import Label, ListItem

from lib.search.grep_result import GrepResult


@dataclass
class Results:
    block_index: int
    lines: List[str] = field(default_factory=list)

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
        self.results_queue = Queue()
        self.list_items_queue = asyncio.Queue()

        self.block_index: int = 0

    async def start_search(self, search_sreen, progress_callback: Callable):
        grep_process: Popen = start_grep_process(
            searched_string=self.searched_lines[0],
            partition=self.partition,
        )
        start_result_enqueue_thread(grep_process, self.results_queue)
        start_result_dequeue_thread(self.dequeue_results, search_sreen)

    def dequeue_results(self, search_sreen):
        loop = asyncio.new_event_loop()
        while True:
            results: Results = self.get_new_results(
                self.results_queue, self.block_index
            )
            self.block_index = results.block_index
            for result in results.lines:
                grep_result = GrepResult(result)
                grep_result.inode = self.fix_block_number(grep_result.inode)
                grep_result.line = self.fix_line_start(grep_result.line)
                grep_result.create_list_item()

                loop.run_until_complete(

                    self.list_items_queue.put(grep_result))
            sleep(0.1)

    def post_result(self, result: str):
        self.new_results_callback(result)

    def get_new_results(self, queue_object: Queue, current_block_index: int) -> Results:
        """Consume grep output queue and format results."""

        queue_list: list = list(queue_object.queue)
        queue_size = len(queue_list)
        queue_object.queue.clear()
        if queue_size == 0:
            return Results(block_index=current_block_index)

        new_block_index: int = current_block_index + queue_size
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

    def fix_line_start(self, line: str) -> str:
        result_index: int = line.find(self.searched_lines[0])
        return line[min(result_index, 15):]

    def fix_block_number(self, block_number: int) -> int:
        """Fix result block number if search string is too far from beginning of
        returned inode number.
        """

        block_number = int(block_number / self.block_size)

        for _ in range(10):
            dd_output: str = decode_result(
                get_dd_output(self.partition, self.block_size, block_number)
            )
            if self.searched_lines[0] in dd_output:
                return block_number
            block_number += 1
        return block_number
