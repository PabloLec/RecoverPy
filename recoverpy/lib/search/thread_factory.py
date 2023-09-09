from __future__ import annotations

from queue import Queue
from subprocess import PIPE, Popen
from threading import Thread
from typing import Callable

from recoverpy.lib.helper import is_dependency_installed
from recoverpy.lib.search.grep_consumer import enqueue_grep_output
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


def start_result_enqueue_thread(
    grep_process: Popen[bytes], queue: Queue[bytes]
) -> None:
    log.debug("thread_factory - Starting result enqueue thread")
    Thread(
        target=enqueue_grep_output,
        args=(grep_process.stdout, queue),
        daemon=True,
        name="enqueue-grep-output-thread",
    ).start()


def start_result_dequeue_thread(dequeue_results: Callable[[], None]) -> None:
    log.debug("thread_factory - Starting result dequeue thread")
    Thread(
        target=dequeue_results,
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
