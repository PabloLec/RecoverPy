from multiprocessing import Queue
from subprocess import Popen, PIPE
from threading import Thread
from typing import Callable

from lib.search.grep_consumer import enqueue_grep_output


def start_grep_process(searched_string: str, partition: str) -> Popen:
    return Popen(
        ["grep", "-a", "-b", f"{searched_string}", partition],
        stdin=None,
        stdout=PIPE,
        stderr=None,
    )


def start_result_enqueue_thread(grep_process: Popen, queue: Queue):
    Thread(
        target=enqueue_grep_output,
        args=(grep_process.stdout, queue),
        daemon=True,
    ).start()


def start_result_dequeue_thread(dequeue_results: Callable):
    Thread(
        target=dequeue_results,
        daemon=True,
    ).start()
