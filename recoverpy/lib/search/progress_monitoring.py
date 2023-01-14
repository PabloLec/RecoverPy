from re import findall
from subprocess import DEVNULL, check_output
from time import sleep

from recoverpy.models.search_progress import SearchProgress


def monitor_search_progress(grep_pid: int, progress: SearchProgress) -> None:
    while True:
        output: str = get_progress_output(grep_pid)

        if not output:
            progress.progress_percent = 100.0

        percent: list = findall(r"(\d+\.\d+)%", output)

        if not percent:
            continue

        progress.progress_percent = float(percent[0])
        sleep(0.5)


def get_progress_output(grep_pid: int) -> str:
    return check_output(["progress", "-p", str(grep_pid)], stderr=DEVNULL).decode(
        "utf8"
    )
