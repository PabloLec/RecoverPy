import io
import re
import time
from queue import Queue
from subprocess import DEVNULL, PIPE, Popen, check_output
from threading import Thread

from recoverpy.utils import helper
from recoverpy.utils.logger import LOGGER


def monitor_progress(search_screen, grep_pid: int):
    """Use 'progress' tool to monitor grep advancement.

    Args:
        search_screen (SearchScreen): Current PyCUI search screen
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
            if len(output) == 0:
                search_screen.grep_progress = "100% - Search completed"
                search_screen.set_title()
                if search_screen.blockindex == 0:
                    search_screen.master.title_bar.set_color(22)
                else:
                    search_screen.master.title_bar.set_color(30)
                return
            continue

        search_screen.grep_progress = progress
        LOGGER.write("debug", f"Progress: {progress}")
        search_screen.set_title()
        time.sleep(1)


def start_search(search_screen):
    """Launch (called within screen_results.__init__):

    - Process executing the grep command.
    - If available, thread using 'progress' tool to monitor grep.
    - Thread to store the grep output in a queue object.
    - Thread to populate the result box dynamically.

    Args:
        search_screen (SearchScreen): Current PyCUI search screen
    """
    grep_process = create_grep_process(
        searched_string=search_screen.searched_string,
        partition=search_screen.partition,
    )

    if helper.is_installed(command="progress"):
        monitor_progress_thread = Thread(
            target=monitor_progress,
            args=(
                search_screen,
                grep_process.pid,
            ),
        )
        monitor_progress_thread.daemon = True
        monitor_progress_thread.start()
        LOGGER.write("debug", "Started progress thread")

    enqueue_grep_output_thread = Thread(
        target=enqueue_grep_output,
        args=(grep_process.stdout, search_screen.queue_object),
        daemon=True,
    )
    enqueue_grep_output_thread.start()

    LOGGER.write("debug", "Started searching thread")

    yield_results_thread = Thread(
        target=search_screen.dequeue_results,
        daemon=True,
    )
    yield_results_thread.start()

    LOGGER.write("debug", "Started output fetching thread")


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
    """Store grep command output in a queue object.

    Args:
        out (io.BufferedReader): Output of grep process
        queue (Queue): Queue object to store stdout
    """
    for line in iter(out.readline, b""):
        queue.put(line)
    out.close()


def yield_new_results(queue_object: Queue, blockindex: int) -> tuple:
    """Probe the queue object for new results.

    If any, returns it to populate the result box.

    Args:
        queue_object (Queue): Queue object storing grep stdout
        blockindex (int): [Current result list index

    Returns:
        tuple: Tuple with (List of new results, New result index)
    """
    # Returns if no new result
    if len(list(queue_object.queue)) == blockindex:
        return None

    queue_list = list(queue_object.queue)

    new_results = queue_list[blockindex:]

    blockindex = len(queue_list)

    return new_results, blockindex
