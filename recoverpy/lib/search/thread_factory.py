from __future__ import annotations

from io import BufferedReader
from queue import Queue
from subprocess import PIPE, Popen
from threading import Thread
from typing import Callable

from recoverpy.lib.helper import is_dependency_installed
from recoverpy.lib.search.progress_monitoring import monitor_search_progress
from recoverpy.log.logger import log
from recoverpy.models.search_progress import SearchProgress


def start_grep_process(searched_string: str, partition: str) -> Popen[bytes]:
    log.debug(f"thread_factory - Starting grep process for {searched_string}")
    return Popen(
        ["grep", "-a", "-b", f"{searched_string}", partition],
        stdin=None,
        stdout=PIPE,
        stderr=None,
    )


def start_grep_stdout_consumer_thread(
    consume_function: Callable[[BufferedReader, Queue[bytes]], None],
    grep_process: Popen[bytes],
    queue: Queue[bytes],
) -> None:
    log.debug("thread_factory - Starting grep stdout consumer thread")
    Thread(
        target=consume_function,
        args=(grep_process.stdout, queue),
        daemon=True,
        name="enqueue-grep-output-thread",
    ).start()


def start_result_formatter_thread(format_function: Callable[[], None]) -> None:
    log.debug("thread_factory - Starting result formatter thread")
    Thread(
        target=format_function,
        daemon=True,
        name="dequeue-results-thread",
    ).start()


def start_progress_monitoring_thread(
    grep_process: Popen[bytes], progress: SearchProgress
) -> None:
    if not is_dependency_installed(command="progress"):
        log.debug("thread_factory - progress not installed, skipping progress thread")
        return

    log.debug("thread_factory - Starting progress monitoring thread")
    Thread(
        target=monitor_search_progress,
        args=(grep_process.pid, progress),
        daemon=True,
        name="progress-monitoring-thread",
    ).start()
