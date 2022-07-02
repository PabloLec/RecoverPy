from io import BufferedReader
from queue import Queue
from re import findall
from subprocess import DEVNULL, PIPE, Popen, check_output
from threading import Thread
from time import sleep

from recoverpy.lib.helper import decode_result, get_inode, is_dependency_installed
from recoverpy.lib.meta_singleton import SingletonMeta
from recoverpy.ui.screen import Screen


class Results:
    def __init__(self, lines: list = list(), block_index: int = 0):
        self.lines: list = lines
        self.block_index: int = block_index

    def is_empty(self):
        return len(self.lines) == 0


class SearchEngine(metaclass=SingletonMeta):
    """Core search class spawning a grep process and multiple threads to monitor
    and consume its output.
    """

    def start_search(self, search_screen: Screen):
        self.partition: str = search_screen.partition
        self.block_size: int = search_screen.block_size
        self.searched_lines: list = search_screen.searched_string.strip().splitlines()
        self.is_multineline: bool = len(self.searched_lines) > 1
        grep_process: Popen = self.start_grep_process(
            searched_string=self.searched_lines[0],
            partition=self.partition,
        )

        self.start_progress_monitoring_thread(grep_process, search_screen)
        self.start_result_enqueue_thread(grep_process, search_screen)
        self.start_result_dequeue_thread(search_screen)

    def start_grep_process(self, searched_string: str, partition: str) -> Popen:
        return Popen(
            ["grep", "-a", "-b", f"{searched_string}", partition],
            stdin=None,
            stdout=PIPE,
            stderr=None,
        )

    def start_progress_monitoring_thread(
        self, grep_process: Popen, search_screen: Screen
    ):
        if not is_dependency_installed(command="progress"):
            return

        Thread(
            target=self.monitor_search_progress,
            args=(search_screen, grep_process.pid),
            daemon=True,
        ).start()

    def start_result_enqueue_thread(self, grep_process: Popen, search_screen: Screen):
        Thread(
            target=self.enqueue_grep_output,
            args=(grep_process.stdout, search_screen.queue_object),
            daemon=True,
        ).start()

    def start_result_dequeue_thread(self, search_screen: Screen):
        Thread(
            target=search_screen.dequeue_results,
            daemon=True,
        ).start()

    def monitor_search_progress(self, search_screen: Screen, grep_pid: int):
        while True:
            output: str = check_output(
                ["progress", "-p", str(grep_pid)], stderr=DEVNULL
            ).decode("utf8")

            if not output:
                search_screen.set_title("100% - Search completed")
                return

            progress: list = findall(r"([0-9]+\.[0-9]+\%[^\)]+\))", output)
            if not progress:
                continue

            search_screen.set_title(progress[0])
            sleep(1)

    def enqueue_grep_output(self, out: BufferedReader, queue: Queue):
        for line in iter(out.readline, b""):
            queue.put(line)
        out.close()

    def get_new_results(self, queue_object: Queue, current_blockindex: int) -> Results:
        """Consume grep output queue and format results."""

        if len(list(queue_object.queue)) == current_blockindex:
            return Results()

        queue_list: list = list(queue_object.queue)
        new_block_index: int = len(queue_list)
        new_results: list = queue_list[current_blockindex:]
        one_lined_results: list = self.format_multine_line_results(new_results)

        if not self.is_multineline:
            return Results(lines=one_lined_results, block_index=new_block_index)

        final_results = [
            result
            for result in one_lined_results
            if self.is_result_format_valid(result)
        ]
        return Results(lines=final_results, block_index=new_block_index)

    def format_multine_line_results(self, results: list) -> list:
        """Format all new results to fit in one line."""

        decoded_results = [decode_result(r) for r in results]
        inodes_indexes = [
            i for i, x in enumerate(decoded_results) if get_inode(x) is not None
        ]

        full_results = []
        for i, inode_index in enumerate(inodes_indexes):
            if i == len(inodes_indexes) - 1:
                full_results.append("".join(decoded_results[inode_index:]))
            else:
                stop_index = inodes_indexes[i + 1]
                full_results.append("".join(decoded_results[inode_index:stop_index]))

        return full_results

    def is_result_format_valid(self, result) -> bool:
        """Check if all searched lines are present in result block and next adjacent
        block, else result is a false positive and will not be displayed.
        """

        inode: int = int(get_inode(result))
        block_output: bytes = self.get_dd_output(
            self.partition, self.block_size * 8, int(inode / (self.block_size * 8))
        )
        next_block_output: bytes = self.get_dd_output(
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
                self.get_dd_output(self.partition, self.block_size, fixed_block)
            )
            if self.searched_lines[0] in dd_output:
                return str(fixed_block)
            fixed_block += 1
        return block_number

    def get_dd_output(
        self, partition: str, block_size: int, block_number: int
    ) -> bytes:
        return check_output(
            [
                "dd",
                f"if={partition}",
                "count=1",
                "status=none",
                f"bs={block_size}",
                f"skip={block_number}",
            ]
        )
