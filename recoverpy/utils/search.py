from io import BufferedReader
from queue import Queue
from re import findall
from subprocess import DEVNULL, PIPE, Popen, check_output
from threading import Thread
from time import sleep

from recoverpy.ui.screen import Screen
from recoverpy.utils.helper import decode_result, get_inode, is_dependency_installed
from recoverpy.utils.logger import LOGGER


class SearchEngine:
    def start_search(self, search_screen: Screen):
        self.partition: str = search_screen.partition
        self.block_size: int = search_screen.block_size
        self.searched_lines: list = search_screen.searched_string.strip().splitlines()
        self.is_multineline: bool = len(self.searched_lines) > 1
        grep_process: Popen = self.create_grep_process(
            searched_string=self.searched_lines[0],
            partition=self.partition,
        )

        self.start_progress_monitoring_thread(grep_process, search_screen)
        self.start_result_enqueue_thread(grep_process, search_screen)
        self.start_result_dequeue_thread(search_screen)

    def create_grep_process(self, searched_string: str, partition: str) -> Popen:
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
        LOGGER.write("debug", "Started progress monitoring thread")

    def start_result_enqueue_thread(self, grep_process: Popen, search_screen: Screen):
        Thread(
            target=self.enqueue_grep_output,
            args=(grep_process.stdout, search_screen.queue_object),
            daemon=True,
        ).start()
        LOGGER.write("debug", "Started grep searching thread")

    def start_result_dequeue_thread(self, search_screen: Screen):
        Thread(
            target=search_screen.dequeue_results,
            daemon=True,
        ).start()
        LOGGER.write("debug", "Started grep output fetching thread")

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

            LOGGER.write("debug", f"Progress: {progress[0]}")
            search_screen.set_title(progress[0])
            sleep(1)

    def enqueue_grep_output(self, out: BufferedReader, queue: Queue):
        for line in iter(out.readline, b""):
            queue.put(line)
        out.close()

    def get_new_results(self, queue_object: Queue, current_blockindex: int) -> tuple:
        if len(list(queue_object.queue)) == current_blockindex:
            return tuple()

        queue_list: list = list(queue_object.queue)
        new_blockindex: int = len(queue_list)
        new_results: list = queue_list[current_blockindex:]
        one_lined_results: list = self.format_multine_line_results(new_results)

        if not self.is_multineline:
            return one_lined_results, new_blockindex

        final_results = [
            result
            for result in one_lined_results
            if self.verify_multiline_result(result)
        ]
        return final_results, new_blockindex

    def verify_multiline_result(self, result):
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

    def format_multine_line_results(self, results: list) -> list:
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

    def fix_block_number(self, block_number: str) -> str:
        fixed_block = int(block_number)
        for _ in range(10):
            dd_output: str = decode_result(
                self.get_dd_output(self.partition, self.block_size, str(fixed_block))
            )
            if self.searched_lines[0] in dd_output:
                return str(fixed_block)
            fixed_block += 1
        return block_number

    def get_dd_output(
        self, partition: str, block_size: int, block_number: str
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


SEARCH_ENGINE: SearchEngine = SearchEngine()
