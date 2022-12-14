from io import BufferedReader
from queue import Queue
from re import findall
from subprocess import DEVNULL, PIPE, Popen, check_output
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING, Callable

from models.progress import Progress

if TYPE_CHECKING:
    from recoverpy.ui.screens.screen_search import SearchScreen

from lib.helper import decode_result, get_inode, is_dependency_installed


def start_grep_process(searched_string: str, partition: str) -> Popen:
    return Popen(
        ["grep", "-a", "-b", f"{searched_string}", partition],
        stdin=None,
        stdout=PIPE,
        stderr=None,
    )


def start_result_dequeue_thread(dequeue_results: Callable):
    Thread(
        target=dequeue_results,
        daemon=True,
    ).start()


def monitor_search_progress(progress: Progress, grep_pid: int):
    while True:
        output: str = check_output(
            ["progress", "-p", str(grep_pid)], stderr=DEVNULL
        ).decode("utf8")

        if not output:
            progress.percent = 100.0
            return

        percent: list = findall(r"(\d+\.\d+%[^)]+\))", output)
        if not percent:
            continue

        progress.percent = float(percent[0])
        sleep(1)


def enqueue_grep_output(out: BufferedReader, queue: Queue):
    for line in iter(out.readline, b""):
        queue.put(line)
    out.close()


def start_result_enqueue_thread(grep_process: Popen, queue: Queue):
    Thread(
        target=enqueue_grep_output,
        args=(grep_process.stdout, queue),
        daemon=True,
    ).start()


def start_progress_monitoring_thread(
    grep_process: Popen, progress: Progress
):
    if not is_dependency_installed(command="progress"):
        return

    Thread(
        target=monitor_search_progress,
        args=(progress, grep_process.pid),
        daemon=True,
    ).start()


def format_multine_line_results(results: list) -> list:
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


def get_dd_output(partition: str, block_size: int, block_number: int) -> bytes:
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
