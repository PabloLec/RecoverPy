import asyncio
from io import BufferedReader
from queue import Queue
from re import findall
from subprocess import DEVNULL, PIPE, Popen, check_output
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING, Callable

from models.progress import Progress

from lib.helper import decode_result, get_inode, is_dependency_installed




def monitor_search_progress(progress: Progress, grep_pid: int, callback: Callable):
    while True:
        output: str = check_output(
            ["progress", "-p", str(grep_pid)], stderr=DEVNULL
        ).decode("utf8")

        if not output:
            progress.percent = 100.0
            callback(progress)
            return

        percent: list = findall(r"(\d+\.\d+%[^)]+\))", output)
        if not percent:
            continue

        progress.percent = float(percent[0])
        callback(progress)
        sleep(0.5)








def start_progress_monitoring_thread(
        grep_process: Popen, callback: Callable
):
    if not is_dependency_installed(command="progress"):
        return

    progress = Progress()
    print("Starting progress monitoring thread")
    Thread(
        target=monitor_search_progress,
        args=(progress, grep_process.pid, callback),
        daemon=True,
    ).start()

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
