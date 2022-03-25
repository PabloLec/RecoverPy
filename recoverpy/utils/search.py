from io import BufferedReader
from queue import Queue
from re import findall
from subprocess import DEVNULL, PIPE, Popen, check_output
from threading import Thread
from time import sleep

from recoverpy.ui.screen import Screen
from recoverpy.utils.helper import is_dependency_installed
from recoverpy.utils.logger import LOGGER


class SearchEngine:
    def start_search(self, search_screen: Screen):
        grep_process: Popen = self.create_grep_process(
            searched_string=search_screen.searched_string,
            partition=search_screen.partition,
        )

        self.start_progress_monitoring_thread(grep_process, search_screen)
        self.start_result_enqueue_thread(grep_process, search_screen)
        self.start_result_dequeue_thread(grep_process, search_screen)

    def create_grep_process(self, searched_string: str, partition: str) -> Popen:
        return Popen(
            ["grep", "-a", "-b", searched_string, partition],
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

    def start_result_dequeue_thread(self, grep_process: Popen, search_screen: Screen):
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
            return None

        queue_list: list = list(queue_object.queue)
        new_blockindex: int = len(queue_list)
        new_results: list = queue_list[current_blockindex:]

        return new_results, new_blockindex


SEARCH_ENGINE: SearchEngine = SearchEngine()
