from queue import Queue
from subprocess import Popen
from time import sleep
from typing import Optional

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

    def __init__(self, partition: str, searched_string: str):
        self.partition: str = partition
        self.block_size: int = get_block_size(partition)
        self.searched_lines: list = searched_string.strip().splitlines()
        self.is_multi_line: Optional[bool] = len(self.searched_lines) > 1

        self.queue = Queue()
        self.block_index: int = 0

    def start_search(self):
        grep_process: Popen = start_grep_process(
            searched_string=self.searched_lines[0],
            partition=self.partition,
        )
        progress = Progress()
        start_progress_monitoring_thread(grep_process, progress)
        start_result_enqueue_thread(grep_process, self.queue)
        start_result_dequeue_thread(self.dequeue_results)

    def dequeue_results(self):
        while True:
            results: Results = self.get_new_results(
                self.queue, self.block_index
            )
            if results.is_empty():
                sleep(1)
                continue
            self.block_index = results.block_index

            #self.add_results_to_list(new_results=results.lines)
            #self.set_title()

            # Sleep to avoid unnecessary overload
            sleep(0.5)

    def get_new_results(self, queue_object: Queue, current_blockindex: int) -> Results:
        """Consume grep output queue and format results."""

        if len(list(queue_object.queue)) == current_blockindex:
            return Results()

        queue_list: list = list(queue_object.queue)
        new_block_index: int = len(queue_list)
        new_results: list = queue_list[current_blockindex:]
        one_lined_results: list = format_multine_line_results(new_results)

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
