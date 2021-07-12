from queue import Queue
from threading import Thread

import io
import re
import time

from subprocess import PIPE, DEVNULL, Popen, check_output
from recoverpy import helper as _HELPER
from recoverpy.logger import LOGGER as _LOGGER


def monitor_progress(search_view, grep_pid: int):
    """Use 'progress' tool to monitor grep advancement.

    Args:
        search_view (SearchView): Current PyCUI search view
        grep_pid (int): PID of grep process
    """

    while True:
        output = check_output(
            ["progress", "-p", str(grep_pid)],
            stderr=DEVNULL,
        ).decode("utf8")

        try:
            progress = re.findall(r"([0-9]+\.[0-9]+\%[^\)]+\))", output)[0]
        except IndexError:
            continue

        search_view.grep_progress = progress
        _LOGGER.write("debug", f"Progress: {progress}")
        search_view.set_title()
        time.sleep(1)


def start_search(search_view):
    """Function is called within view_results.__init__
    Launches:
    - Process executing the grep command.
    - If available, thread using 'progress' tool to monitor grep.
    - Thread to store the grep output in a queue object.
    - Thread to populate the result box dynamically.

    Args:
        search_view (SearchView): Current PyCUI search view
    """

    grep_process = create_grep_process(
        searched_string=search_view.searched_string,
        partition=search_view.partition,
    )

    if _HELPER.is_progress_installed():
        monitor_progress_thread = Thread(
            target=monitor_progress,
            args=(
                search_view,
                grep_process.pid,
            ),
        )
        monitor_progress_thread.daemon = True
        monitor_progress_thread.start()

    enqueue_grep_output_thread = Thread(
        target=enqueue_grep_output,
        args=(grep_process.stdout, search_view.queue_object),
        daemon=True,
    )
    enqueue_grep_output_thread.start()

    _LOGGER.write("debug", "Started searching thread")

    yield_results_thread = Thread(
        target=search_view.populate_result_list,
        daemon=True,
    )
    yield_results_thread.start()

    _LOGGER.write("debug", "Started output fetching thread")


def create_grep_process(searched_string: str, partition: str) -> Popen:
    """Instantiate a process executing the grep search.

    Args:
        searched_string (str): String to search
        partition (str): Partition to search into

    Returns:
        Popen: Created process
    """

    return Popen(
        ["grep", "-a", "-b", searched_string, partition],
        stdin=None,
        stdout=PIPE,
        stderr=None,
    )


def enqueue_grep_output(out: io.BufferedReader, queue: Queue):
    """Function called in a thread to store the grep command output in
    a queue object.

    Args:
        out (io.BufferedReader): Output of grep process
        queue (Queue): Queue object to store stdout
    """

    for line in iter(out.readline, b""):
        queue.put(line)
    out.close()


def yield_new_results(queue_object: Queue, result_index: int) -> tuple:
    """Probe the queue object for new results.
    If any, returns it to populate the result box.

    Args:
        queue_object (Queue): Queue object storing grep stdout
        result_index (int): [Current result list index

    Returns:
        tuple: Tuple with 1. List of new results 2. New result index
    """

    # Returns if no new result
    if len(list(queue_object.queue)) == result_index:
        return None

    queue_list = list(queue_object.queue)

    new_results = [queue_element for queue_element in queue_list[result_index:]]

    result_index = len(queue_list)

    return new_results, result_index
